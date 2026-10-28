using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

namespace DaoSurvivor
{
    /// <summary>Unity adapter: rendering, input and events around the independently testable RunModel.</summary>
    public sealed class SurvivorCombat : MonoBehaviour
    {
        public Action<CombatSnapshot> Updated;
        public Action<UpgradeChoice[]> LevelUp;
        public Action<RunResult> Ended;
        public bool EffectsEnabled = true;
        [Range(0, .3f)] public float TopHudFraction = .18f;
        [Range(0, .2f)] public float BottomHudFraction = .10f;
        public RunModel Model { get; private set; }
        public CombatSnapshot Snapshot { get { return Model == null ? new CombatSnapshot { status = "idle" } : Model.Snapshot(); } }

        private readonly Dictionary<string, Sprite> sprites = new Dictionary<string, Sprite>();
        private readonly Dictionary<int, SpriteRenderer> enemyViews = new Dictionary<int, SpriteRenderer>();
        private readonly Dictionary<int, SpriteRenderer> shotViews = new Dictionary<int, SpriteRenderer>();
        private readonly Dictionary<int, SpriteRenderer> dropViews = new Dictionary<int, SpriteRenderer>();
        private readonly List<TransientEffect> transientEffects = new List<TransientEffect>();
        private readonly HashSet<int> activeIds = new HashSet<int>();
        private readonly List<int> staleIds = new List<int>();
        private Transform worldRoot;
        private SpriteRenderer playerView;
        private SpriteRenderer arenaView;
        private Camera gameCamera;
        private bool ownsCamera;
        private Sprite whiteSprite;
        private Texture2D whiteTexture;
        private Font numberFont;
        private float notifyTimer;
        private Vector2 touchOrigin, touchMove, externalMove;
        private int touchId = -1;
        private bool draggingMouse;
        private Color fieldColor;

        private sealed class TransientEffect
        {
            public GameObject obj;
            public float life, fullLife;
            public TextMesh label;
            public SpriteRenderer renderer;
            public float targetSize;
        }

        public void Begin(string character, string stage, int attackBonus = 0, int healthBonus = 0, int speedBonus = 0)
        {
            StopRun();
            Model = new RunModel(); Model.Begin(character, stage, attackBonus, healthBonus, speedBonus);
            EnsureRendering();
            worldRoot.gameObject.SetActive(true);
            fieldColor = stage == "moon" ? new Color(.76f, .85f, .82f) : stage == "ruins" ? new Color(.85f, .82f, .72f) : new Color(.87f, .88f, .75f);
            gameCamera.backgroundColor = fieldColor;
            arenaView = MakeRenderer("道场手绘场景板", GetArenaArt());
            arenaView.sortingOrder = -100;
            playerView = MakeRenderer("道友", GetArt(character == "jianxiu" ? "sword" : character == "lingxiu" ? "healer" : "hero"));
            SetHeight(playerView, 1.13f);
            playerView.transform.position = Position(Model.PlayerX, Model.PlayerY);
            notifyTimer = 0; Updated?.Invoke(Model.Snapshot());
        }

        private void EnsureRendering()
        {
            if (worldRoot == null)
            {
                var root = new GameObject("CombatWorld"); root.transform.SetParent(transform, false); worldRoot = root.transform;
            }
            gameCamera = Camera.main;
            if (gameCamera == null)
            {
                var cameraObject = new GameObject("SurvivorCamera"); gameCamera = cameraObject.AddComponent<Camera>();
                cameraObject.tag = "MainCamera"; ownsCamera = true;
            }
            gameCamera.orthographic = true; gameCamera.clearFlags = CameraClearFlags.SolidColor;
            gameCamera.nearClipPlane = .1f; gameCamera.farClipPlane = 100;
            gameCamera.transform.position = new Vector3(9, -5.75f, -10);
            gameCamera.transform.rotation = Quaternion.identity;
            if (whiteSprite == null)
            {
                whiteTexture = new Texture2D(1, 1, TextureFormat.RGBA32, false);
                whiteTexture.SetPixel(0, 0, Color.white); whiteTexture.Apply();
                whiteSprite = Sprite.Create(whiteTexture, new Rect(0, 0, 1, 1), new Vector2(.5f, .5f), 1);
            }
            if (numberFont == null) numberFont = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        }

        private Sprite GetArt(string name)
        {
            Sprite result; if (sprites.TryGetValue(name, out result)) return result;
            var texture = Resources.Load<Texture2D>("DaoArt/" + name);
            if (texture == null)
            {
                Debug.LogError("Missing required DaoArt texture: " + name);
                return null;
            }
            result = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, .1f), 100);
            result.name = name; sprites.Add(name, result); return result;
        }

        private Sprite GetArenaArt()
        {
            Sprite result; if (sprites.TryGetValue("arena-v1", out result)) return result;
            var texture = Resources.Load<Texture2D>("DaoArt/arena-v1");
            if (texture == null)
            {
                Debug.LogError("Missing DaoArt/arena-v1 hand-painted scene plate; plain-color fallback remains visible.");
                sprites.Add("arena-v1", null); return null;
            }
            result = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, .5f), 100);
            result.name = "arena-v1"; sprites.Add("arena-v1", result); return result;
        }

        private void FitArenaToCamera()
        {
            if (arenaView == null || arenaView.sprite == null) return;
            float height = gameCamera.orthographicSize * 2;
            Vector2 nativeSize = arenaView.sprite.bounds.size;
            float scale = Mathf.Max(height * gameCamera.aspect / nativeSize.x, height / nativeSize.y);
            arenaView.transform.localScale = new Vector3(scale, scale, 1);
            arenaView.transform.position = new Vector3(gameCamera.transform.position.x, gameCamera.transform.position.y, 0);
        }

        private SpriteRenderer MakeRenderer(string name, Sprite sprite)
        {
            var go = new GameObject(name); go.transform.SetParent(worldRoot, false);
            var view = go.AddComponent<SpriteRenderer>(); view.sprite = sprite; return view;
        }

        private static void SetHeight(SpriteRenderer renderer, float height)
        {
            if (renderer.sprite == null) return;
            float scale = height / renderer.sprite.bounds.size.y;
            renderer.transform.localScale = new Vector3(scale, scale, 1);
        }

        private static Vector3 Position(float x, float y) { return new Vector3(x / 100f, -y / 100f, 0); }

        public void SetPaused(bool paused)
        {
            if (Model == null) return;
            Model.SetPaused(paused); ResetInput(); Updated?.Invoke(Model.Snapshot());
        }

        public void ChooseUpgrade(string id)
        {
            if (Model == null || !Model.ChooseUpgrade(id)) return;
            ProcessEvents(); Updated?.Invoke(Model.Snapshot());
        }

        public void SetMoveInput(Vector2 input) { externalMove = Vector2.ClampMagnitude(input, 1); }

        public void DamagePlayer(float amount)
        {
            if (Model == null) return;
            Model.DamagePlayer(amount); ProcessEvents(); Updated?.Invoke(Model.Snapshot());
        }

        public void GrantExperience(float amount)
        {
            if (Model == null) return;
            Model.AddXp(amount); ProcessEvents(); Updated?.Invoke(Model.Snapshot());
        }

        public void StopRun()
        {
            if (Model != null) Model.Stop(); ResetInput();
            if (worldRoot != null)
            {
                for (int i = worldRoot.childCount - 1; i >= 0; i--)
                {
                    var child = worldRoot.GetChild(i).gameObject;
                    child.SetActive(false); Destroy(child);
                }
                worldRoot.gameObject.SetActive(false);
            }
            enemyViews.Clear(); shotViews.Clear(); dropViews.Clear(); transientEffects.Clear(); playerView = null; arenaView = null;
        }

        private void ResetInput() { touchMove = Vector2.zero; externalMove = Vector2.zero; touchId = -1; draggingMouse = false; }

        private void Update()
        {
            if (Model == null || Model.Status == "idle") return;
            float aspect = Mathf.Max(.3f, gameCamera.aspect);
            gameCamera.orthographicSize = Mathf.Max(6.35f, 9.5f / aspect);
            FitArenaToCamera();
            // World units per screen fraction; reserve HUD space plus the actual sprite pivot extents.
            float visibleHeight = gameCamera.orthographicSize * 2;
            float safeTop = gameCamera.transform.position.y + gameCamera.orthographicSize - visibleHeight * TopHudFraction;
            float safeBottom = gameCamera.transform.position.y - gameCamera.orthographicSize + visibleHeight * BottomHudFraction;
            Model.SetPlayerBounds(30, -(safeTop - 1.13f * .9f) * 100,
                RunModel.WorldWidth - 30, -(safeBottom + 1.13f * .1f) * 100);
            if (Model.Status == "running")
            {
                var input = ReadInput();
                Model.Step(UnityEngine.Time.deltaTime, input.x, -input.y);
                ProcessEvents();
                notifyTimer -= UnityEngine.Time.unscaledDeltaTime;
                if (notifyTimer <= 0) { notifyTimer = .08f; Updated?.Invoke(Model.Snapshot()); }
            }
            RenderActors();
            if (Model.Status == "running") UpdateEffects(UnityEngine.Time.deltaTime);
        }

        private Vector2 ReadInput()
        {
            Vector2 keys = Vector2.zero;
            if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) keys.x--;
            if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) keys.x++;
            if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) keys.y++;
            if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) keys.y--;
            if (Input.touchCount > 0)
            {
                for (int i = 0; i < Input.touchCount; i++)
                {
                    var touch = Input.GetTouch(i);
                    if (touch.phase == TouchPhase.Began && touchId < 0 && !PointerOverUi(touch.fingerId))
                    { touchId = touch.fingerId; touchOrigin = touch.position; }
                    if (touch.fingerId != touchId) continue;
                    if (touch.phase == TouchPhase.Ended || touch.phase == TouchPhase.Canceled)
                    { touchMove = Vector2.zero; touchId = -1; }
                    else touchMove = Vector2.ClampMagnitude((touch.position - touchOrigin) / (Screen.dpi > 0 ? Screen.dpi * .28f : 70), 1);
                }
            }
            else
            {
                if (Input.GetMouseButtonDown(0) && !PointerOverUi(-1)) { draggingMouse = true; touchOrigin = Input.mousePosition; }
                if (draggingMouse && Input.GetMouseButton(0)) touchMove = Vector2.ClampMagnitude(((Vector2)Input.mousePosition - touchOrigin) / 75f, 1);
                if (Input.GetMouseButtonUp(0)) { draggingMouse = false; touchMove = Vector2.zero; }
            }
            return Vector2.ClampMagnitude(keys + touchMove + externalMove, 1);
        }

        private static bool PointerOverUi(int pointerId)
        {
            return EventSystem.current != null && (pointerId >= 0 ? EventSystem.current.IsPointerOverGameObject(pointerId) : EventSystem.current.IsPointerOverGameObject());
        }

        private void ProcessEvents()
        {
            foreach (var evt in Model.TakeEvents())
            {
                if (evt.type == "levelup") { ResetInput(); LevelUp?.Invoke(evt.choices); }
                else if (evt.type == "end") { ResetInput(); Updated?.Invoke(Model.Snapshot()); Ended?.Invoke(evt.result); }
                else if (evt.type == "hit" && EffectsEnabled) FloatingNumber(evt.x, evt.y, Mathf.RoundToInt(evt.amount).ToString(), new Color(1, .95f, .65f));
                else if (evt.type == "hurt" && EffectsEnabled) FloatingNumber(evt.x, evt.y, "-" + Mathf.RoundToInt(evt.amount), new Color(.85f, .2f, .12f));
                else if (evt.type == "pulse" && EffectsEnabled) PulseEffect(evt.x, evt.y, evt.amount / 100f);
            }
        }

        private void RenderActors()
        {
            if (playerView == null) return;
            var position = Position(Model.PlayerX, Model.PlayerY);
            if (EffectsEnabled && Model.Status == "running") position.y += Mathf.Sin(Model.Time * 8) * .022f;
            playerView.transform.position = position;
            var scale = playerView.transform.localScale;
            scale.x = Mathf.Abs(scale.x) * Model.Facing; playerView.transform.localScale = scale;
            playerView.sortingOrder = (int)Model.PlayerY;
            playerView.color = Model.Invulnerability > 0 ? new Color(1, .65f, .55f, .7f + .3f * Mathf.Sin(Model.Time * 40)) : Color.white;
            activeIds.Clear();
            foreach (var enemy in Model.Enemies)
            {
                activeIds.Add(enemy.id); SpriteRenderer view;
                if (!enemyViews.TryGetValue(enemy.id, out view))
                {
                    view = MakeRenderer("妖灵_" + enemy.id, GetArt(enemy.type == "lantern" ? "enemy-lantern" : "enemy-tiger"));
                    SetHeight(view, enemy.elite ? .95f : .67f); enemyViews.Add(enemy.id, view);
                }
                var p = Position(enemy.x, enemy.y);
                if (EffectsEnabled && Model.Status == "running") p.y += Mathf.Sin(Model.Time * 6 + enemy.bob) * .025f;
                view.transform.position = p; view.sortingOrder = (int)enemy.y;
                view.color = enemy.flash > 0 ? new Color(1, .6f, .4f) : Color.white;
                view.flipX = enemy.x > Model.PlayerX;
            }
            RemoveStale(enemyViews);
            activeIds.Clear();
            foreach (var shot in Model.Projectiles)
            {
                activeIds.Add(shot.id); SpriteRenderer view;
                if (!shotViews.TryGetValue(shot.id, out view))
                {
                    view = MakeRenderer("飞剑_" + shot.id, whiteSprite);
                    view.color = new Color(1, .84f, .35f, .9f); view.transform.localScale = new Vector3(.44f, .065f, 1);
                    view.sortingOrder = 1500; shotViews.Add(shot.id, view);
                }
                view.transform.position = Position(shot.x, shot.y);
                view.transform.rotation = Quaternion.Euler(0, 0, -Mathf.Atan2(shot.vy, shot.vx) * Mathf.Rad2Deg);
            }
            RemoveStale(shotViews);
            activeIds.Clear();
            foreach (var drop in Model.Drops)
            {
                activeIds.Add(drop.id); SpriteRenderer view;
                if (!dropViews.TryGetValue(drop.id, out view))
                {
                    view = MakeRenderer("灵气_" + drop.id, whiteSprite); view.color = new Color(.2f, .66f, .49f);
                    view.transform.localScale = Vector3.one * .105f; view.transform.rotation = Quaternion.Euler(0, 0, 45);
                    view.sortingOrder = 5; dropViews.Add(drop.id, view);
                }
                view.transform.position = Position(drop.x, drop.y);
            }
            RemoveStale(dropViews);
        }

        private void RemoveStale(Dictionary<int, SpriteRenderer> views)
        {
            staleIds.Clear(); foreach (var pair in views) if (!activeIds.Contains(pair.Key)) staleIds.Add(pair.Key);
            foreach (int id in staleIds) { Destroy(views[id].gameObject); views.Remove(id); }
        }

        private void FloatingNumber(float x, float y, string text, Color color)
        {
            if (transientEffects.Count > 45) return;
            var go = new GameObject("Damage"); go.transform.SetParent(worldRoot, false); go.transform.position = Position(x, y) + Vector3.up * .75f;
            var label = go.AddComponent<TextMesh>(); label.text = text; label.font = numberFont;
            label.anchor = TextAnchor.MiddleCenter; label.alignment = TextAlignment.Center;
            label.fontSize = 36; label.characterSize = .045f; label.color = color;
            var renderer = go.GetComponent<MeshRenderer>(); renderer.sharedMaterial = numberFont.material; renderer.sortingOrder = 2000;
            transientEffects.Add(new TransientEffect { obj = go, label = label, life = .65f, fullLife = .65f });
        }

        private void PulseEffect(float x, float y, float radius)
        {
            var view = MakeRenderer("太极震", whiteSprite); view.transform.position = Position(x, y); view.sortingOrder = 0;
            view.color = new Color(.4f, .75f, .55f, .18f);
            transientEffects.Add(new TransientEffect { obj = view.gameObject, renderer = view, life = .4f, fullLife = .4f, targetSize = radius * 2 });
        }

        private void UpdateEffects(float dt)
        {
            for (int i = transientEffects.Count - 1; i >= 0; i--)
            {
                var fx = transientEffects[i]; fx.life -= dt;
                if (fx.life <= 0) { Destroy(fx.obj); transientEffects.RemoveAt(i); continue; }
                if (fx.label != null)
                {
                    fx.obj.transform.position += Vector3.up * dt * .35f;
                    var color = fx.label.color; color.a = fx.life / fx.fullLife; fx.label.color = color;
                }
                else if (fx.renderer != null)
                {
                    fx.obj.transform.localScale = Vector3.one * Mathf.Lerp(.2f, fx.targetSize, 1 - fx.life / fx.fullLife);
                    var color = fx.renderer.color; color.a = .18f * fx.life / fx.fullLife; fx.renderer.color = color;
                }
            }
        }

        private void OnApplicationFocus(bool focused) { if (!focused && Model != null && Model.Status == "running") SetPaused(true); }
        private void OnApplicationPause(bool paused) { if (paused && Model != null && Model.Status == "running") SetPaused(true); }
        private void OnDisable()
        {
            if (Model != null && Model.Status == "running") SetPaused(true);
            else ResetInput();
        }
        private void OnDestroy()
        {
            if (Model != null) Model.Stop();
            foreach (var sprite in sprites.Values) if (sprite != null) Destroy(sprite);
            if (whiteSprite != null) Destroy(whiteSprite); if (whiteTexture != null) Destroy(whiteTexture);
            if (ownsCamera && gameCamera != null) Destroy(gameCamera.gameObject);
        }
    }
}
