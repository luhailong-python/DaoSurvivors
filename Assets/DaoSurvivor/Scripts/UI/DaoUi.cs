using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace DaoSurvivor
{
    internal static class DaoUi
    {
        internal static Font Font;
        internal static readonly Color Ink = new Color(.12f, .25f, .19f);
        internal static readonly Color Muted = new Color(.43f, .45f, .34f);
        internal static readonly Color Ivory = new Color(1, .96f, .82f);
        internal static readonly Color Gold = new Color(.77f, .61f, .30f);
        internal static readonly Color Jade = new Color(.12f, .35f, .28f);
        private static readonly Dictionary<string, Sprite> Sprites = new Dictionary<string, Sprite>();

        internal static RectTransform Node(string name, Transform parent, float x, float y, float width, float height)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = go.GetComponent<RectTransform>(); rt.SetParent(parent, false);
            rt.anchorMin = rt.anchorMax = new Vector2(0, 1); rt.pivot = new Vector2(0, 1);
            rt.anchoredPosition = new Vector2(x, -y); rt.sizeDelta = new Vector2(width, height);
            return rt;
        }

        internal static RectTransform Fill(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            var rt = go.GetComponent<RectTransform>(); rt.SetParent(parent, false);
            rt.anchorMin = Vector2.zero; rt.anchorMax = Vector2.one;
            rt.offsetMin = rt.offsetMax = Vector2.zero;
            return rt;
        }

        internal static RectTransform Stage(string name, Transform parent)
        {
            var rt = Node(name, parent, 0, 0, 1920, 1080);
            rt.anchorMin = rt.anchorMax = new Vector2(.5f, .5f); rt.pivot = new Vector2(.5f, .5f);
            rt.anchoredPosition = Vector2.zero; return rt;
        }

        internal static Sprite Art(string name)
        {
            Sprite sprite; if (Sprites.TryGetValue(name, out sprite)) return sprite;
            var texture = Resources.Load<Texture2D>("DaoArt/" + name);
            if (texture == null) { Debug.LogError("Missing UI DaoArt texture: " + name); return null; }
            Vector4 border = Vector4.zero;
            switch (name)
            {
                case "main_frame": border = new Vector4(76, 79, 76, 79); break;
                case "title_plate": border = new Vector4(142, 29, 142, 35); break;
                case "section_plate": border = new Vector4(76, 16, 72, 21); break;
                case "member_row": border = new Vector4(24, 19, 24, 19); break;
                case "application_card": border = new Vector4(27, 24, 27, 24); break;
                case "button_primary": case "button_secondary": border = new Vector4(45, 16, 45, 16); break;
            }
            sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(.5f, .5f), 100, 0, SpriteMeshType.FullRect, border);
            sprite.name = name; Sprites.Add(name, sprite); return sprite;
        }

        internal static Image Picture(string name, Transform parent, float x, float y, float width, float height, string art, bool preserve = true)
        {
            var rt = Node(name, parent, x, y, width, height); var image = rt.gameObject.AddComponent<Image>();
            image.sprite = Art(art); image.preserveAspect = preserve; image.raycastTarget = false;
            return image;
        }

        internal static Image Panel(string name, Transform parent, float x, float y, float width, float height, string art = "main_frame")
        {
            var image = Picture(name, parent, x, y, width, height, art, false);
            image.type = Image.Type.Sliced; return image;
        }

        internal static Image Block(string name, Transform parent, float x, float y, float width, float height, Color color)
        {
            var rt = Node(name, parent, x, y, width, height); var image = rt.gameObject.AddComponent<Image>();
            image.color = color; image.raycastTarget = false; return image;
        }

        internal static Text Label(string name, Transform parent, float x, float y, float width, float height, string value, int size = 24, Color? color = null, TextAnchor alignment = TextAnchor.UpperLeft)
        {
            // Noto CJK's ascent/descent is larger than its visible ink. Reserve a full line box,
            // while keeping the original center/bottom when aligning labels inside controls.
            int lines = EstimatedLines(value, width, size);
            float measuredHeight = Mathf.Max(height, lines * size * 1.7f);
            int verticalAlignment = (int)alignment / 3;
            if (verticalAlignment == 1) y -= (measuredHeight - height) * .5f;
            else if (verticalAlignment == 2) y -= measuredHeight - height;
            height = measuredHeight;
            var rt = Node(name, parent, x, y, width, height); var text = rt.gameObject.AddComponent<Text>();
            text.font = Font; text.fontSize = size; text.color = color ?? Ink; text.text = value;
            text.alignment = alignment; text.supportRichText = false; text.raycastTarget = false;
            text.horizontalOverflow = HorizontalWrapMode.Wrap; text.verticalOverflow = VerticalWrapMode.Overflow;
            text.lineSpacing = 1; return text;
        }

        private static int EstimatedLines(string value, float width, int size)
        {
            if (string.IsNullOrEmpty(value)) return 1;
            int lines = 0;
            foreach (string paragraph in value.Split('\n'))
            {
                float advance = 0;
                foreach (char c in paragraph) advance += size * (c > 255 ? 1f : .56f);
                lines += Mathf.Max(1, Mathf.CeilToInt(advance / Mathf.Max(1, width)));
            }
            return lines;
        }

        internal static Button Button(string name, Transform parent, float x, float y, float width, float height, string value, UnityAction action, bool primary = false, int size = 25)
        {
            var image = Panel(name, parent, x, y, width, height, primary ? "button_primary" : "button_secondary"); image.raycastTarget = true;
            var button = image.gameObject.AddComponent<Button>(); button.targetGraphic = image;
            var colors = button.colors;
            colors.normalColor = Color.white; colors.highlightedColor = new Color(1, .97f, .85f);
            colors.pressedColor = new Color(.78f, .88f, .77f); colors.selectedColor = new Color(1, .98f, .9f);
            colors.disabledColor = new Color(.72f, .72f, .69f, .65f); button.colors = colors;
            if (action != null) button.onClick.AddListener(action);
            Label(name + "-text", image.transform, 14, 5, width - 28, height - 10, value, size, primary ? Ivory : Ink, TextAnchor.MiddleCenter);
            return button;
        }

        internal static Button CloseButton(Transform parent, float x, float y, UnityAction action)
        {
            var image = Picture("close", parent, x, y, 66, 66, "close"); image.raycastTarget = true;
            var button = image.gameObject.AddComponent<Button>(); button.targetGraphic = image;
            button.onClick.AddListener(action); return button;
        }

        internal static Image Bar(string name, Transform parent, float x, float y, float width, float height, Color color)
        {
            var background = Block(name + "-track", parent, x, y, width, height, new Color(.15f, .27f, .2f, .13f));
            var fill = Block(name + "-fill", background.transform, 0, 0, width, height, color);
            return fill;
        }

        internal static void ClearChildren(Transform parent)
        {
            for (int i = parent.childCount - 1; i >= 0; i--)
            {
                var child = parent.GetChild(i).gameObject; child.SetActive(false); Object.Destroy(child);
            }
        }

        internal static void Release()
        {
            foreach (var sprite in Sprites.Values) if (sprite != null) Object.Destroy(sprite);
            Sprites.Clear();
        }
    }
}
