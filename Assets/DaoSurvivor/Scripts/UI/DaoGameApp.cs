using System;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace DaoSurvivor
{
    /// <summary>Self-contained native UGUI shell. Dynamic copy and interactions are never baked into artwork.</summary>
    public sealed class DaoGameApp : MonoBehaviour
    {
        public SurvivorCombat Combat { get; private set; }
        private Canvas canvas;
        private RectTransform menuLayer, battleLayer, modalLayer;
        private PlayerProgress progress;
        private string character = "qingyun", stage = "bamboo", currentTab = "adventure", currentModal = "";
        private string settingsReturnModal = "", helpReturnModal = "", abandonReturnModal = "pause";
        private UpgradeChoice[] pendingChoices;
        private RunResult pendingResult;
        private RunResult lastRecordedResult;
        private bool rewardClaimed, suppressPauseModal;
        private Text hpText, xpText, timerText, killsText, skillsText;
        private Image hpFill, xpFill;
        private AudioSource audioSource;
        private AudioClip clickClip;

        private sealed class CharacterInfo
        {
            internal string id, art, name, role, description;
            internal int hp, attack, speed;
            internal string FullName { get { return id == "qingyun" ? "青云小道" : id == "jianxiu" ? "逍遥剑修" : "清莲灵修"; } }
            internal CharacterInfo(string id, string art, string name, string role, string description, int hp, int attack, int speed)
            { this.id = id; this.art = art; this.name = name; this.role = role; this.description = description; this.hp = hp; this.attack = attack; this.speed = speed; }
        }
        private static readonly CharacterInfo[] Characters = {
            new CharacterInfo("qingyun", "hero", "青云", "太极符道", "以符御气，攻守均衡。适合初次入山的道友。", 120, 28, 205),
            new CharacterInfo("jianxiu", "sword", "剑修", "御剑游侠", "双剑齐出，身法轻盈。以灵巧步法穿行妖阵。", 100, 22, 220),
            new CharacterInfo("lingxiu", "healer", "灵修", "回春灵修", "气血充盈，每五秒缓缓回春。道途从容长久。", 150, 25, 185)
        };
        private static readonly string[] StageIds = { "bamboo", "ruins", "moon" };
        private static readonly string[] StageNames = { "翠竹幽谷", "古观遗址", "月下莲池" };
        private static readonly string[] StageHints = { "入门 · 妖灵较缓", "进阶 · 妖灵更坚韧", "挑战 · 妖灵更迅捷" };

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindAnyObjectByType<DaoGameApp>() == null) new GameObject("DaoSurvivors").AddComponent<DaoGameApp>();
        }

        private void Awake()
        {
            DontDestroyOnLoad(gameObject);
            Application.targetFrameRate = 60;
            progress = PlayerProgress.Load();
            // Persist the initial 120-stone gift once; restarting never grants it again.
            progress.Save();
            DaoUi.Font = Resources.Load<Font>("Fonts/NotoSansSC-Regular");
            if (DaoUi.Font == null)
            {
                Debug.LogError("Missing Fonts/NotoSansSC-Regular: Chinese UI requires its bundled font.");
                DaoUi.Font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }
            if (FindAnyObjectByType<EventSystem>() == null)
            {
                var system = new GameObject("DaoEventSystem", typeof(EventSystem), typeof(StandaloneInputModule));
                DontDestroyOnLoad(system);
            }
            var canvasGo = new GameObject("DaoCanvas", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
            canvasGo.transform.SetParent(transform, false); canvas = canvasGo.GetComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay; canvas.sortingOrder = 100;
            var scaler = canvasGo.GetComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1920, 1080); scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.Expand;
            menuLayer = DaoUi.Fill("Menu", canvas.transform);
            battleLayer = DaoUi.Fill("BattleHud", canvas.transform); battleLayer.gameObject.SetActive(false);
            modalLayer = DaoUi.Fill("ModalLayer", canvas.transform);
            Combat = gameObject.AddComponent<SurvivorCombat>(); Combat.EffectsEnabled = progress.effects;
            Combat.Updated += OnSnapshot; Combat.LevelUp += ShowUpgrade; Combat.Ended += ShowResult;
            PrepareAudio(); ShowTab("adventure");
        }

        private void PrepareAudio()
        {
            if (FindAnyObjectByType<AudioListener>() == null) gameObject.AddComponent<AudioListener>();
            audioSource = gameObject.AddComponent<AudioSource>(); audioSource.playOnAwake = false; audioSource.spatialBlend = 0;
            const int sampleRate = 22050, length = 1764;
            var samples = new float[length];
            for (int i = 0; i < length; i++) samples[i] = Mathf.Sin(i * 2 * Mathf.PI * 880 / sampleRate) * .055f * (1 - i / (float)length);
            clickClip = AudioClip.Create("JadeClick", length, 1, sampleRate, false); clickClip.SetData(samples, 0);
        }

        private void Click(Action action)
        {
            if (progress.sound && audioSource != null && clickClip != null) audioSource.PlayOneShot(clickClip);
            action?.Invoke();
        }

        private Button Button(string name, Transform parent, float x, float y, float width, float height, string text, Action action, bool primary = false, int size = 25)
        { return DaoUi.Button(name, parent, x, y, width, height, text, () => Click(action), primary, size); }

        public void ShowTab(string tab)
        {
            if (Combat != null && Combat.Model != null && Combat.Model.Status != "idle" && Combat.Model.Status != "ended") return;
            currentTab = tab == "training" || tab == "codex" ? tab : "adventure";
            CloseModal(); menuLayer.gameObject.SetActive(true); battleLayer.gameObject.SetActive(false);
            DaoUi.ClearChildren(menuLayer); BuildBackground();
            var screen = DaoUi.Stage("MenuLayout", menuLayer); BuildHeader(screen);
            if (currentTab == "training") BuildTraining(screen);
            else if (currentTab == "codex") BuildCodex(screen);
            else BuildAdventure(screen);
            BuildNavigation(screen);
        }

        private void BuildBackground()
        {
            var background = DaoUi.Fill("LobbyArtwork", menuLayer);
            background.anchorMin = background.anchorMax = new Vector2(.5f, .5f);
            background.pivot = new Vector2(.5f, .5f); background.anchoredPosition = Vector2.zero;
            background.sizeDelta = Vector2.zero;
            var image = background.gameObject.AddComponent<RawImage>(); image.texture = Resources.Load<Texture2D>("DaoArt/lobby-v1"); image.raycastTarget = false;
            if (image.texture != null)
            {
                var fitter = background.gameObject.AddComponent<AspectRatioFitter>();
                fitter.aspectMode = AspectRatioFitter.AspectMode.EnvelopeParent;
                fitter.aspectRatio = image.texture.width / (float)image.texture.height;
            }
            var shade = DaoUi.Fill("BackgroundTint", menuLayer).gameObject.AddComponent<Image>();
            shade.color = new Color(.04f, .15f, .12f, .09f); shade.raycastTarget = false;
        }

        private void BuildHeader(Transform screen)
        {
            DaoUi.Block("HeaderJade", screen, 0, 0, 1920, 106, new Color(.05f, .23f, .19f, .94f));
            DaoUi.Block("HeaderGoldLine", screen, 0, 104, 1920, 2, DaoUi.Gold);
            DaoUi.Picture("TaijiMark", screen, 58, 22, 62, 62, "icon-taiji");
            DaoUi.Label("GameTitle", screen, 139, 24, 410, 50, "道途幸存者", 36, DaoUi.Ivory, TextAnchor.MiddleLeft);
            DaoUi.Label("Genre", screen, 532, 33, 420, 35, "一念入道 · 万妖退散", 20, new Color(.8f, .85f, .73f), TextAnchor.MiddleLeft);
            DaoUi.Panel("Currency", screen, 1265, 23, 270, 61, "button_secondary");
            DaoUi.Picture("CurrencyIcon", screen, 1287, 37, 32, 32, "icon-taiji");
            DaoUi.Label("CurrencyValue", screen, 1331, 28, 180, 45, "灵石  " + progress.coins.ToString("N0"), 25, DaoUi.Ink, TextAnchor.MiddleCenter);
            Button("help", screen, 1560, 23, 130, 61, "指引", OpenHelp, false, 22);
            Button("settings", screen, 1714, 23, 150, 61, "设置", OpenSettings, false, 22);
        }

        private void BuildAdventure(Transform screen)
        {
            DaoUi.Label("AdventureTag", screen, 100, 156, 870, 38, "道家 Q 版 · 肉鸽生存", 24, DaoUi.Ivory);
            DaoUi.Label("Slogan", screen, 98, 724, 1000, 112, "执一念，御万妖", 72, new Color(1, .95f, .78f));
            DaoUi.Label("SloganDetail", screen, 105, 845, 870, 76, "一炉丹火，一身道法。\n在万千妖灵之间，走出自己的道途。", 25, DaoUi.Ivory);
            string record = progress.completedRuns == 0 ? "初始赠送 120 灵石，可前往修行精进道法" : "最高击败 " + progress.bestKills + "  ·  最长历练 " + Clock(progress.bestTime) + "  ·  通关 " + progress.wins + " 次";
            DaoUi.Label("BestRecord", screen, 106, 938, 950, 35, record, 20, new Color(.91f, .9f, .75f));
            DaoUi.Panel("AdventureWindow", screen, 1150, 165, 690, 780);
            DaoUi.Picture("AdventureTitlePlate", screen, 1240, 141, 510, 103, "title_plate");
            DaoUi.Label("AdventureTitle", screen, 1310, 167, 370, 55, "出山历练", 36, DaoUi.Ivory, TextAnchor.MiddleCenter);
            DaoUi.Label("ChooseCharacter", screen, 1200, 248, 590, 32, "一 · 结缘道友", 24);
            for (int i = 0; i < Characters.Length; i++)
            {
                var data = Characters[i]; bool selected = character == data.id;
                var card = DaoUi.Panel("character-" + data.id, screen, 1199 + i * 202, 289, 188, 140, selected ? "button_primary" : "application_card");
                card.raycastTarget = true; var button = card.gameObject.AddComponent<Button>(); button.targetGraphic = card;
                button.onClick.AddListener(() => Click(() => { character = data.id; ShowTab("adventure"); }));
                DaoUi.Picture("Portrait", card.transform, 35, 5, 118, 97, data.art);
                DaoUi.Label("Name", card.transform, 15, 102, 158, 31, data.name, 23, selected ? DaoUi.Ivory : DaoUi.Ink, TextAnchor.MiddleCenter);
            }
            var hero = CurrentCharacter();
            DaoUi.Label("CharacterRole", screen, 1202, 449, 588, 46, hero.FullName + " · " + hero.role, 27);
            DaoUi.Label("CharacterDescription", screen, 1202, 490, 588, 44, hero.description, 19, DaoUi.Muted);
            DaoUi.Panel("CharacterStats", screen, 1200, 540, 590, 47, "member_row");
            DaoUi.Label("Stats", screen, 1218, 546, 554, 34,
                "气血 " + (hero.hp + progress.healthLevel * 10) + "    伤害 " + Mathf.RoundToInt(hero.attack * (1 + progress.attackLevel * .05f)) + "    身法 " + Mathf.RoundToInt(hero.speed * (1 + progress.speedLevel * .03f)),
                20, DaoUi.Ink, TextAnchor.MiddleCenter);
            DaoUi.Label("ChooseStage", screen, 1200, 607, 370, 33, "二 · 选择秘境", 24);
            DaoUi.Label("DurationNote", screen, 1588, 611, 202, 29, "每局 90 秒", 19, DaoUi.Muted, TextAnchor.MiddleRight);
            for (int i = 0; i < StageIds.Length; i++)
            {
                string id = StageIds[i]; bool selected = stage == id;
                var button = Button("stage-" + id, screen, 1196, 649 + i * 70, 600, 58, "", () => { stage = id; ShowTab("adventure"); }, selected);
                DaoUi.Label("StageName", button.transform, 33, 7, 240, 42, StageNames[i], 24, selected ? DaoUi.Ivory : DaoUi.Ink, TextAnchor.MiddleLeft);
                DaoUi.Label("StageHint", button.transform, 265, 9, 293, 38, StageHints[i], 18, selected ? DaoUi.Ivory : DaoUi.Muted, TextAnchor.MiddleRight);
            }
            var start = Button("start-run", screen, 1208, 872, 574, 65, "入 山 历 练", BeginRun, true, 29);
            if (EventSystem.current != null) EventSystem.current.SetSelectedGameObject(start.gameObject);
        }

        private void BuildNavigation(Transform screen)
        {
            Button("nav-adventure", screen, 622, 989, 210, 66, "历练", () => ShowTab("adventure"), currentTab == "adventure");
            Button("nav-training", screen, 855, 989, 210, 66, "修行", () => ShowTab("training"), currentTab == "training");
            Button("nav-codex", screen, 1088, 989, 210, 66, "图鉴", () => ShowTab("codex"), currentTab == "codex");
            DaoUi.Label("LocalMode", screen, 1430, 1005, 380, 34, "本地单人 · 存档自动保存", 19, DaoUi.Ivory, TextAnchor.MiddleRight);
        }

        private void BuildTraining(Transform screen)
        {
            DaoUi.Panel("TrainingWindow", screen, 170, 182, 1580, 750);
            DaoUi.Picture("TrainingTitlePlate", screen, 653, 147, 614, 124, "title_plate");
            DaoUi.Label("TrainingTitle", screen, 760, 179, 400, 57, "温养根基", 37, DaoUi.Ivory, TextAnchor.MiddleCenter);
            DaoUi.Label("TrainingIntro", screen, 360, 294, 1200, 46, "积微成道。消耗灵石精进根基，永久加成会带入下一次历练。", 25, DaoUi.Ink, TextAnchor.MiddleCenter);
            TrainingCard(screen, 272, "attack", "淬炼道法", "icon-sword", "每级法术伤害 +5%", "伤害加成 +" + progress.attackLevel * 5 + "%");
            TrainingCard(screen, 753, "health", "固本培元", "icon-taiji", "每级气血上限 +10", "气血加成 +" + progress.healthLevel * 10);
            TrainingCard(screen, 1234, "speed", "御风行步", "icon-boots", "每级移动速度 +3%", "身法加成 +" + progress.speedLevel * 3 + "%");
            DaoUi.Label("TrainingGift", screen, 350, 857, 1220, 34, "初始赠送 120 灵石；更多灵石通过历练结算获得。每项最多五级。", 20, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        private void TrainingCard(Transform parent, float x, string id, string title, string icon, string description, string current)
        {
            int level = progress.LevelOf(id), cost = progress.CostOf(id);
            var card = DaoUi.Panel("training-" + id, parent, x, 366, 414, 454, "application_card");
            DaoUi.Picture("TrainingIcon", card.transform, 130, 28, 154, 154, icon);
            DaoUi.Label("Title", card.transform, 35, 194, 344, 44, title, 31, DaoUi.Ink, TextAnchor.MiddleCenter);
            DaoUi.Label("Level", card.transform, 40, 245, 334, 31, "境界 " + level + " / 5", 21, DaoUi.Muted, TextAnchor.MiddleCenter);
            DaoUi.Label("Effect", card.transform, 30, 290, 354, 36, current, 24, DaoUi.Ink, TextAnchor.MiddleCenter);
            DaoUi.Label("NextEffect", card.transform, 30, 331, 354, 30, description, 19, DaoUi.Muted, TextAnchor.MiddleCenter);
            var button = Button("train-" + id, card.transform, 47, 378, 320, 59, level >= 5 ? "已至圆满" : (progress.coins >= cost ? "精进 · " : "灵石不足 · ") + cost + " 灵石", () =>
            {
                if (progress.TryTrain(id)) ShowTab("training");
            }, level < 5 && progress.coins >= cost, 22);
            button.interactable = level < 5 && progress.coins >= cost;
        }

        private void BuildCodex(Transform screen)
        {
            DaoUi.Panel("CodexWindow", screen, 170, 182, 1580, 750);
            DaoUi.Picture("CodexTitlePlate", screen, 653, 147, 614, 124, "title_plate");
            DaoUi.Label("CodexTitle", screen, 760, 179, 400, 57, "山海灵图", 37, DaoUi.Ivory, TextAnchor.MiddleCenter);
            DaoUi.Label("CodexIntro", screen, 350, 292, 1220, 40, "认得道友，也识妖灵。每一段道途，都始于一份了解。", 25, DaoUi.Ink, TextAnchor.MiddleCenter);
            string[] arts = { "hero", "sword", "healer", "enemy-tiger", "enemy-lantern", "icon-sword", "icon-boots", "icon-taiji" };
            string[] names = { "青云", "剑修", "灵修", "符小虎", "桂灯童", "桃木飞剑", "踏云履", "太极玉" };
            string[] copy = {
                "太极符道。符剑自动寻敌，攻守均衡。", "御剑游侠。双剑齐出，步法轻快。", "回春灵修。气血充盈，每五秒回复。",
                "循着灵气而来，靠近道友时造成接触伤害。", "漂浮的妖灵。小心成群接近，留出退路。",
                "飞剑道法的法器意象；万剑归宗增加投射数。", "身法道法的法器意象；凌波步提高移动速度。", "太极道法的法器意象；太极震震退身边妖灵。"
            };
            for (int i = 0; i < arts.Length; i++)
            {
                int column = i % 4, row = i / 4;
                var card = DaoUi.Panel("codex-" + arts[i], screen, 237 + column * 369, 357 + row * 260, 340, 238, "application_card");
                DaoUi.Picture("Art", card.transform, 22, 18, 118, 140, arts[i]);
                DaoUi.Label("Name", card.transform, 154, 38, 162, 72, names[i], 26, DaoUi.Ink, TextAnchor.MiddleLeft);
                DaoUi.Label("Description", card.transform, 25, 168, 290, 60, copy[i], 17, DaoUi.Muted);
            }
            DaoUi.Label("CodexNote", screen, 350, 891, 1220, 25, "法器图用于道法说明；本轮人物与妖灵为高清静态素材。", 17, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        public void BeginRun()
        {
            if (Combat.Model != null && Combat.Model.Status != "idle" && Combat.Model.Status != "ended") return;
            CloseModal(); pendingChoices = null; pendingResult = null; lastRecordedResult = null; rewardClaimed = false;
            menuLayer.gameObject.SetActive(false); battleLayer.gameObject.SetActive(true); BuildBattleHud();
            Combat.EffectsEnabled = progress.effects;
            Combat.Begin(character, stage, progress.attackLevel, progress.healthLevel, progress.speedLevel);
        }

        private void BuildBattleHud()
        {
            DaoUi.ClearChildren(battleLayer); var screen = DaoUi.Stage("BattleLayout", battleLayer);
            DaoUi.Panel("HudPaper", screen, 27, 20, 1866, 149);
            DaoUi.Picture("HudPortrait", screen, 52, 36, 90, 112, CurrentCharacter().art);
            DaoUi.Label("HudCharacter", screen, 157, 43, 400, 34, CurrentCharacter().name + " · " + StageName(stage), 25);
            hpText = DaoUi.Label("HpText", screen, 158, 85, 450, 30, "", 20);
            hpFill = DaoUi.Bar("Hp", screen, 158, 126, 440, 14, new Color(.26f, .55f, .39f));
            xpText = DaoUi.Label("XpText", screen, 681, 66, 380, 35, "", 23, DaoUi.Ink, TextAnchor.MiddleCenter);
            xpFill = DaoUi.Bar("Xp", screen, 688, 126, 366, 14, new Color(.81f, .65f, .28f));
            timerText = DaoUi.Label("Time", screen, 1120, 51, 240, 65, "00:00", 42, DaoUi.Ink, TextAnchor.MiddleCenter);
            DaoUi.Label("Duration", screen, 1130, 121, 220, 27, "目标 01:30", 17, DaoUi.Muted, TextAnchor.MiddleCenter);
            killsText = DaoUi.Label("Kills", screen, 1390, 69, 220, 58, "击败 0", 27, DaoUi.Ink, TextAnchor.MiddleCenter);
            Button("pause", screen, 1667, 65, 178, 62, "暂 歇", PauseRun, true, 24);
            DaoUi.Panel("CombatFooter", screen, 27, 980, 1866, 74, "member_row");
            skillsText = DaoUi.Label("Skills", screen, 63, 1001, 1130, 37, "初始道法 · 自动飞剑", 20);
            DaoUi.Label("MoveHint", screen, 1222, 1001, 628, 37, "WASD / 方向键移动 · 也可按住拖动", 19, DaoUi.Muted, TextAnchor.MiddleRight);
        }

        private void OnSnapshot(CombatSnapshot snapshot)
        {
            if (!isActiveAndEnabled || !battleLayer.gameObject.activeSelf) return;
            if (hpText != null) hpText.text = "气血 " + Mathf.CeilToInt(snapshot.hp) + " / " + Mathf.CeilToInt(snapshot.maxHp);
            if (xpText != null) xpText.text = "道法 " + snapshot.level + " 阶 · 灵气 " + (int)snapshot.xp + " / " + (int)snapshot.xpNext;
            if (timerText != null) timerText.text = Clock(snapshot.time);
            if (killsText != null) killsText.text = "击败 " + snapshot.kills;
            if (hpFill != null) hpFill.rectTransform.sizeDelta = new Vector2(440 * (snapshot.maxHp > 0 ? Mathf.Clamp01(snapshot.hp / snapshot.maxHp) : 0), 14);
            if (xpFill != null) xpFill.rectTransform.sizeDelta = new Vector2(366 * (snapshot.xpNext > 0 ? Mathf.Clamp01(snapshot.xp / snapshot.xpNext) : 0), 14);
            if (skillsText != null) skillsText.text = UpgradeSummary(snapshot.upgrades);
            if (snapshot.status == "paused" && currentModal == "" && !suppressPauseModal) ShowPause();
        }

        public void PauseRun()
        {
            if (Combat.Model == null || (Combat.Model.Status != "running" && Combat.Model.Status != "paused")) return;
            suppressPauseModal = true; Combat.SetPaused(true); suppressPauseModal = false; ShowPause();
        }

        public void ResumeRun()
        {
            if (Combat.Model == null || Combat.Model.Status != "paused") return;
            CloseModal(); Combat.SetPaused(false);
        }

        private RectTransform ModalWindow(string kind, string title, float width, float height)
        {
            CloseModal(); currentModal = kind;
            var blocker = DaoUi.Fill("ModalBlocker", modalLayer).gameObject.AddComponent<Image>();
            blocker.color = new Color(.025f, .10f, .08f, .72f); blocker.raycastTarget = true;
            var screen = DaoUi.Stage("ModalLayout", modalLayer);
            float x = (1920 - width) / 2, y = (1080 - height) / 2;
            DaoUi.Panel(kind + "-window", screen, x, y, width, height);
            DaoUi.Picture("ModalPlaque", screen, 660, y - 35, 600, 122, "title_plate");
            DaoUi.Label("ModalTitle", screen, 755, y - 2, 410, 54, title, 36, DaoUi.Ivory, TextAnchor.MiddleCenter);
            return screen;
        }

        private void CloseModal()
        {
            if (modalLayer != null) DaoUi.ClearChildren(modalLayer);
            currentModal = "";
        }

        private void ShowPause()
        {
            var screen = ModalWindow("pause", "稍作调息", 720, 590);
            DaoUi.Label("PausePoem", screen, 660, 369, 600, 45, "山中无岁月，且听风一程。", 26, DaoUi.Muted, TextAnchor.MiddleCenter);
            Button("resume", screen, 751, 455, 418, 72, "继续历练", ResumeRun, true, 28);
            Button("pause-settings", screen, 751, 555, 418, 67, "画面与音效", OpenSettings);
            Button("return-home", screen, 751, 650, 418, 67, "结束历练", ReturnHome);
            DaoUi.Label("PauseFrozen", screen, 660, 751, 600, 31, "暂停期间，历练计时与妖灵行动均已停止", 18, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        private void ShowUpgrade(UpgradeChoice[] choices)
        {
            pendingChoices = choices;
            var screen = ModalWindow("upgrade", "灵光乍现", 1430, 670);
            DaoUi.Label("UpgradeHint", screen, 500, 315, 920, 43, "选择一道法，继续本次历练", 27, DaoUi.Muted, TextAnchor.MiddleCenter);
            for (int i = 0; i < choices.Length; i++)
            {
                var choice = choices[i];
                var card = DaoUi.Panel("upgrade-" + choice.id, screen, 320 + i * 440, 390, 400, 390, "application_card");
                DaoUi.Picture("UpgradeArt", card.transform, 137, 18, 126, 126, UpgradeArt(choice.id));
                DaoUi.Label("UpgradeTitle", card.transform, 20, 156, 360, 48, choice.title, 29, DaoUi.Ink, TextAnchor.MiddleCenter);
                DaoUi.Label("UpgradeLevel", card.transform, 35, 213, 330, 29, "领悟第 " + choice.nextLevel + " 重", 19, DaoUi.Muted, TextAnchor.MiddleCenter);
                DaoUi.Label("UpgradeDescription", card.transform, 35, 248, 330, 72, choice.description, 21, DaoUi.Ink, TextAnchor.MiddleCenter);
                Button("choose-" + choice.id, card.transform, 54, 328, 292, 56, "领悟此法", () => { CloseModal(); Combat.ChooseUpgrade(choice.id); }, true, 24);
            }
            DaoUi.Label("UpgradePaused", screen, 500, 827, 920, 30, "道法抉择期间，历练已暂停", 18, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        private void ShowResult(RunResult result)
        {
            if (ReferenceEquals(lastRecordedResult, result)) return;
            lastRecordedResult = result;
            pendingResult = result; rewardClaimed = false;
            progress.completedRuns++; if (result.victory) progress.wins++;
            progress.bestKills = Mathf.Max(progress.bestKills, result.kills); progress.bestTime = Mathf.Max(progress.bestTime, result.time); progress.Save();
            BuildResult();
        }

        private void BuildResult()
        {
            if (pendingResult == null) return;
            var result = pendingResult; var screen = ModalWindow("result", result.victory ? "此境已平" : "道途未尽", 1050, 700);
            DaoUi.Picture("ResultHero", screen, 525, 354, 260, 352, CurrentCharacter().art);
            DaoUi.Label("ResultStage", screen, 840, 349, 530, 47, StageName(result.stage) + " · 历练结算", 29);
            DaoUi.Label("ResultTime", screen, 840, 421, 530, 37, "历练时长    " + Clock(result.time), 26);
            DaoUi.Label("ResultKills", screen, 840, 477, 530, 37, "击败妖灵    " + result.kills, 26);
            DaoUi.Label("ResultLevel", screen, 840, 533, 530, 37, "道法境界    第 " + result.level + " 阶", 26);
            DaoUi.Panel("ResultReward", screen, 837, 600, 530, 86, "member_row");
            DaoUi.Picture("RewardIcon", screen, 866, 619, 47, 47, "icon-taiji");
            DaoUi.Label("RewardValue", screen, 936, 613, 402, 55, "获得灵石  +" + result.coins, 29, DaoUi.Ink, TextAnchor.MiddleCenter);
            Button("return-home", screen, 711, 745, 498, 73, "领取灵石 · 返回山门", ClaimAndHome, true, 27);
            DaoUi.Label("ResultNote", screen, 540, 858, 840, 30, "此行所得皆成修行，下一次出山再见。", 20, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        private void ClaimAndHome()
        {
            if (pendingResult != null && !rewardClaimed)
            { progress.coins += pendingResult.coins; rewardClaimed = true; progress.Save(); }
            GoHome();
        }

        public void ReturnHome()
        {
            if (pendingResult != null && Combat.Model != null && Combat.Model.Status == "ended") { ClaimAndHome(); return; }
            if (Combat.Model == null || Combat.Model.Status == "idle") { GoHome(); return; }
            abandonReturnModal = Combat.Model.Status == "upgrade" ? "upgrade" : "pause";
            suppressPauseModal = true; Combat.SetPaused(true); suppressPauseModal = false;
            var screen = ModalWindow("abandon", "结束本次历练？", 900, 470);
            DaoUi.Label("AbandonExplanation", screen, 605, 426, 710, 108,
                "本次尚未结算，离开后不会获得灵石。\n确认结束当前历练，返回山门吗？", 27, DaoUi.Ink, TextAnchor.MiddleCenter);
            Button("cancel-abandon", screen, 613, 598, 322, 69, "留在此境", RestoreAbandonModal, true, 26);
            Button("confirm-abandon", screen, 982, 598, 322, 69, "结束历练", GoHome, false, 26);
        }

        private void RestoreAbandonModal()
        {
            if (abandonReturnModal == "upgrade" && pendingChoices != null) ShowUpgrade(pendingChoices);
            else ShowPause();
        }

        private void GoHome()
        {
            Combat.StopRun(); pendingChoices = null; pendingResult = null; rewardClaimed = false;
            ShowTab("adventure");
        }

        public void OpenSettings()
        {
            if (currentModal == "settings") return;
            settingsReturnModal = currentModal;
            if (Combat.Model != null && Combat.Model.Status == "running")
            {
                settingsReturnModal = "pause"; suppressPauseModal = true; Combat.SetPaused(true); suppressPauseModal = false;
            }
            BuildSettings();
        }

        private void BuildSettings()
        {
            var screen = ModalWindow("settings", "清心小筑", 820, 590);
            DaoUi.Label("SettingsHint", screen, 650, 368, 620, 42, "调好心境，再赴山海。", 25, DaoUi.Muted, TextAnchor.MiddleCenter);
            Button("toggle-sound", screen, 665, 455, 590, 70, "音效                       " + (progress.sound ? "已开启" : "已关闭"), () => { progress.sound = !progress.sound; progress.Save(); BuildSettings(); }, progress.sound, 25);
            Button("toggle-effects", screen, 665, 555, 590, 70, "特效                       " + (progress.effects ? "已开启" : "已关闭"), () =>
            { progress.effects = !progress.effects; Combat.EffectsEnabled = progress.effects; progress.Save(); BuildSettings(); }, progress.effects, 25);
            Button("settings-done", screen, 759, 697, 402, 65, "调息已毕", CloseSettings, true, 27);
            DaoUi.CloseButton(screen, 1273, 278, () => Click(CloseSettings));
            DaoUi.Label("SettingsNote", screen, 625, 794, 670, 26, "设置保存在本机；调息不会自动结束暂停或道法抉择。", 17, DaoUi.Muted, TextAnchor.MiddleCenter);
        }

        private void CloseSettings()
        {
            string restore = settingsReturnModal; settingsReturnModal = "";
            if (restore == "upgrade" && pendingChoices != null) ShowUpgrade(pendingChoices);
            else if (restore == "pause") ShowPause();
            else if (restore == "result") BuildResult();
            else if (restore == "abandon") ReturnHome();
            else CloseModal();
        }

        private void OpenHelp()
        {
            helpReturnModal = currentModal;
            if (Combat.Model != null && Combat.Model.Status == "running")
            { helpReturnModal = "pause"; suppressPauseModal = true; Combat.SetPaused(true); suppressPauseModal = false; }
            var screen = ModalWindow("help", "入山指引", 1050, 760);
            DaoUi.Label("HelpContent", screen, 575, 324, 770, 430,
                "一 · 选择道友与秘境，开始一局 90 秒历练。\n\n二 · 使用 WASD、方向键，或按住画面拖动来移动。飞剑会自动寻敌。\n\n三 · 靠近绿色灵气即可拾取；积满后，从三道法中选择其一。\n\n四 · 守住气血，撑过 90 秒。结算灵石可用于永久修行。", 23);
            Button("help-done", screen, 758, 810, 404, 66, "我已知晓", CloseHelp, true, 27);
            DaoUi.CloseButton(screen, 1386, 196, () => Click(CloseHelp));
        }

        private void CloseHelp()
        {
            string restore = helpReturnModal; helpReturnModal = "";
            if (restore == "upgrade" && pendingChoices != null) ShowUpgrade(pendingChoices);
            else if (restore == "pause") ShowPause();
            else if (restore == "result") BuildResult();
            else CloseModal();
        }

        private void Update()
        {
            if (!Input.GetKeyDown(KeyCode.Escape)) return;
            if (currentModal == "settings") CloseSettings();
            else if (currentModal == "help") CloseHelp();
            else if (currentModal == "pause") ResumeRun();
            else if (currentModal == "abandon") RestoreAbandonModal();
            else if (currentModal == "" && battleLayer.gameObject.activeSelf) PauseRun();
        }

        private CharacterInfo CurrentCharacter()
        { foreach (var data in Characters) if (data.id == character) return data; return Characters[0]; }
        private static string StageName(string id)
        { for (int i = 0; i < StageIds.Length; i++) if (StageIds[i] == id) return StageNames[i]; return StageNames[0]; }
        private static string Clock(float seconds)
        { int total = Mathf.FloorToInt(Mathf.Max(0, seconds)); return (total / 60).ToString("00") + ":" + (total % 60).ToString("00"); }
        private static string UpgradeArt(string id)
        { return id == "stride" || id == "haste" ? "icon-boots" : id == "power" || id == "multishot" ? "icon-sword" : "icon-taiji"; }
        private static string UpgradeSummary(string[] upgrades)
        {
            if (upgrades == null || upgrades.Length == 0) return "初始道法 · 自动飞剑";
            string result = "道法 · ";
            for (int i = 0; i < upgrades.Length && i < 5; i++)
            {
                var parts = upgrades[i].Split(':'); string name;
                switch (parts[0])
                {
                    case "power": name = "五雷"; break; case "haste": name = "行云"; break;
                    case "multishot": name = "万剑"; break; case "vitality": name = "金光"; break;
                    case "stride": name = "凌波"; break; case "magnet": name = "聚灵"; break;
                    case "pulse": name = "太极"; break; default: name = "回春"; break;
                }
                if (i > 0) result += "  ·  "; result += name + " " + (parts.Length > 1 ? parts[1] : "1") + "重";
            }
            if (upgrades.Length > 5) result += "  等"; return result;
        }

        private void OnDestroy()
        {
            if (Combat != null) { Combat.Updated -= OnSnapshot; Combat.LevelUp -= ShowUpgrade; Combat.Ended -= ShowResult; }
            DaoUi.Release(); if (clickClip != null) Destroy(clickClip);
        }
    }
}
