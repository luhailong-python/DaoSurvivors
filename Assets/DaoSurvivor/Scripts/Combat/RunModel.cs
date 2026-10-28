using System;
using System.Collections.Generic;

namespace DaoSurvivor
{
    [Serializable]
    public sealed class CombatSnapshot
    {
        public float time, duration, hp, maxHp, xp, xpNext;
        public int level, kills, damage;
        public string status, character, stage;
        public string[] upgrades;
    }

    [Serializable]
    public sealed class UpgradeChoice
    {
        public string id, title, description;
        public int nextLevel;
        public UpgradeChoice(string id, string title, string description)
        { this.id = id; this.title = title; this.description = description; }
        public UpgradeChoice Copy(int level)
        { return new UpgradeChoice(id, title, description) { nextLevel = level }; }
    }

    [Serializable]
    public sealed class RunResult
    {
        public bool victory;
        public float time;
        public int kills, level, coins;
        public string character, stage;
    }

    public sealed class CombatActor
    {
        public int id;
        public float x, y, hp, speed, radius, flash, bob;
        public bool elite;
        public string type;
    }

    public sealed class SpellShot
    {
        public int id;
        public float x, y, vx, vy, life, damage;
    }

    public sealed class SpiritDrop
    {
        public int id;
        public float x, y;
        public int value;
        public bool collected;
    }

    public sealed class CombatEvent
    {
        public string type;
        public float x, y, amount;
        public UpgradeChoice[] choices;
        public RunResult result;
    }

    /// <summary>Pure simulation. It has no Unity dependency and can be verified without an editor.</summary>
    public sealed class RunModel
    {
        public const float WorldWidth = 1800f, WorldHeight = 1150f;
        public string Status { get; private set; } = "idle";
        public string Character { get; private set; }
        public string Stage { get; private set; }
        public float Time { get; private set; }
        public float Duration { get; private set; } = 90f;
        public float Hp { get; private set; }
        public float MaxHp { get; private set; }
        public int Level { get; private set; } = 1;
        public int Kills { get; private set; }
        public float Xp { get; private set; }
        public float XpNext { get; private set; } = 6f;
        public float PlayerX { get; private set; } = 900f;
        public float PlayerY { get; private set; } = 575f;
        public int Facing { get; private set; } = 1;
        public float Attack { get; private set; }
        public float Speed { get; private set; }
        public float Invulnerability { get; private set; }
        public float Damage { get; private set; }
        public RunResult Result { get; private set; }
        public UpgradeChoice[] Choices { get; private set; } = new UpgradeChoice[0];
        public readonly List<CombatActor> Enemies = new List<CombatActor>();
        public readonly List<SpellShot> Projectiles = new List<SpellShot>();
        public readonly List<SpiritDrop> Drops = new List<SpiritDrop>();
        public readonly Dictionary<string, int> Upgrades = new Dictionary<string, int>();

        private readonly Random random;
        private readonly List<CombatEvent> events = new List<CombatEvent>();
        private float spawnTimer, attackTimer, interval, pickupRange, pulseTimer, healTimer;
        private float minPlayerX = 30, maxPlayerX = WorldWidth - 30, minPlayerY = 45, maxPlayerY = WorldHeight - 30;
        private int projectileCount, idCounter;
        private static readonly UpgradeChoice[] Definitions = {
            new UpgradeChoice("power", "五雷正法", "法术伤害提升 25%"),
            new UpgradeChoice("haste", "行云流水", "施法间隔缩短 15%"),
            new UpgradeChoice("multishot", "万剑归宗", "每次施法增加 1 枚飞剑"),
            new UpgradeChoice("vitality", "金光护体", "气血上限增加 30，并恢复 30 气血"),
            new UpgradeChoice("stride", "凌波步", "移动速度提升 18%"),
            new UpgradeChoice("magnet", "聚灵阵", "灵气吸取范围增加 65%"),
            new UpgradeChoice("pulse", "太极震", "每 3 秒震退并伤害身边的妖灵"),
            new UpgradeChoice("mend", "回春诀", "恢复 40 气血，每 5 秒回复 4 气血")
        };

        public RunModel(int? seed = null) { random = seed.HasValue ? new Random(seed.Value) : new Random(); }
        public static float Clamp(float value, float min, float max) { return Math.Max(min, Math.Min(max, value)); }
        private static float Distance(float x1, float y1, float x2, float y2)
        { float dx = x1 - x2, dy = y1 - y2; return (float)Math.Sqrt(dx * dx + dy * dy); }
        private float Rand() { return (float)random.NextDouble(); }
        private int UpgradeLevel(string id) { int n; return Upgrades.TryGetValue(id, out n) ? n : 0; }

        public void Begin(string character, string stage, int attackBonus = 0, int healthBonus = 0, int speedBonus = 0, float duration = 90f)
        {
            Character = character == "jianxiu" || character == "lingxiu" ? character : "qingyun";
            Stage = stage == "ruins" || stage == "moon" ? stage : "bamboo";
            Duration = Clamp(duration, 1, 3600);
            Time = 0; Level = 1; Kills = 0; Xp = 0; XpNext = 6; Damage = 0;
            MaxHp = Character == "lingxiu" ? 150 : Character == "jianxiu" ? 100 : 120;
            MaxHp += Clamp(healthBonus, 0, 50) * 10; Hp = MaxHp;
            Attack = (Character == "jianxiu" ? 22 : Character == "lingxiu" ? 25 : 28) * (1 + Clamp(attackBonus, 0, 60) * .05f);
            Speed = (Character == "jianxiu" ? 220 : Character == "lingxiu" ? 185 : 205) * (1 + Clamp(speedBonus, 0, 40) * .03f);
            interval = Character == "jianxiu" ? .78f : Character == "lingxiu" ? .72f : .64f;
            projectileCount = Character == "jianxiu" ? 2 : 1;
            PlayerX = 900; PlayerY = 575; Facing = 1; Invulnerability = 0;
            minPlayerX = 30; maxPlayerX = WorldWidth - 30; minPlayerY = 45; maxPlayerY = WorldHeight - 30;
            pickupRange = 110; spawnTimer = .4f; attackTimer = .15f; pulseTimer = 3; healTimer = 5; idCounter = 0;
            Enemies.Clear(); Projectiles.Clear(); Drops.Clear(); Upgrades.Clear(); events.Clear();
            Choices = new UpgradeChoice[0]; Result = null; Status = "running";
        }

        public void SetPaused(bool paused)
        {
            if (paused && Status == "running") Status = "paused";
            else if (!paused && Status == "paused") Status = "running";
        }

        public void Stop() { Status = "idle"; events.Clear(); Choices = new UpgradeChoice[0]; }
        public CombatEvent[] TakeEvents() { var result = events.ToArray(); events.Clear(); return result; }

        public void SetPlayerBounds(float minX, float minY, float maxX, float maxY)
        {
            minPlayerX = Clamp(minX, 30, WorldWidth - 70);
            maxPlayerX = Clamp(maxX, minPlayerX + 40, WorldWidth - 30);
            minPlayerY = Clamp(minY, 45, WorldHeight - 70);
            maxPlayerY = Clamp(maxY, minPlayerY + 40, WorldHeight - 30);
            PlayerX = Clamp(PlayerX, minPlayerX, maxPlayerX);
            PlayerY = Clamp(PlayerY, minPlayerY, maxPlayerY);
        }

        public bool DamagePlayer(float amount)
        {
            if (Status != "running" || amount <= 0 || Invulnerability > 0) return false;
            Hp = Math.Max(0, Hp - amount); Invulnerability = .7f;
            events.Add(new CombatEvent { type = "hurt", amount = amount, x = PlayerX, y = PlayerY });
            if (Hp <= 0) Finish(false);
            return true;
        }

        private void Finish(bool victory)
        {
            if (Result != null || Status == "idle") return;
            Status = "ended";
            Result = new RunResult { victory = victory, time = Time, kills = Kills, level = Level,
                coins = Math.Max(5, (int)(Kills * 1.5f + Time / 3 + (victory ? 100 : 0))), character = Character, stage = Stage };
            events.Add(new CombatEvent { type = "end", result = Result });
        }

        public void AddXp(float amount)
        {
            if (Status != "running" || amount <= 0) return;
            Xp += amount; CheckLevelUp();
        }

        private void CheckLevelUp()
        {
            if (Status != "running" || Xp < XpNext) return;
            Xp -= XpNext; Level++; XpNext = 6 + (Level - 1) * 4; Status = "upgrade";
            var pool = new List<UpgradeChoice>();
            foreach (var choice in Definitions)
                if (UpgradeLevel(choice.id) < (choice.id == "multishot" ? 4 : 6)) pool.Add(choice);
            for (int i = pool.Count - 1; i > 0; i--) { int j = random.Next(i + 1); var tmp = pool[i]; pool[i] = pool[j]; pool[j] = tmp; }
            // At every cap, offer a repeatable heal rather than leaving the run trapped.
            if (pool.Count == 0) pool.Add(Definitions[Definitions.Length - 1]);
            Choices = new UpgradeChoice[Math.Min(3, pool.Count)];
            for (int i = 0; i < Choices.Length; i++) Choices[i] = pool[i].Copy(UpgradeLevel(pool[i].id) + 1);
            events.Add(new CombatEvent { type = "levelup", choices = Choices });
        }

        public bool ChooseUpgrade(string id)
        {
            if (Status != "upgrade") return false;
            bool found = false; foreach (var choice in Choices) if (choice.id == id) found = true;
            if (!found) return false;
            Upgrades[id] = UpgradeLevel(id) + 1;
            switch (id)
            {
                case "power": Attack *= 1.25f; break;
                case "haste": interval *= .85f; break;
                case "multishot": projectileCount++; break;
                case "vitality": MaxHp += 30; Hp = Math.Min(MaxHp, Hp + 30); break;
                case "stride": Speed *= 1.18f; break;
                case "magnet": pickupRange *= 1.65f; break;
                case "mend": Hp = Math.Min(MaxHp, Hp + 40); break;
            }
            Choices = new UpgradeChoice[0]; Status = "running";
            events.Add(new CombatEvent { type = "upgrade", amount = Upgrades[id] });
            CheckLevelUp(); return true;
        }

        private void SpawnEnemy()
        {
            float angle = Rand() * (float)Math.PI * 2, radius = 480 + Rand() * 160;
            bool elite = Time > 30 && Rand() < .13f;
            float healthFactor = Stage == "ruins" ? 1.22f : Stage == "moon" ? 1.12f : 1;
            float speedFactor = Stage == "moon" ? 1.24f : Stage == "ruins" ? 1.05f : 1;
            Enemies.Add(new CombatActor { id = ++idCounter,
                x = Clamp(PlayerX + (float)Math.Cos(angle) * radius, 20, WorldWidth - 20),
                y = Clamp(PlayerY + (float)Math.Sin(angle) * radius, 20, WorldHeight - 20),
                hp = (elite ? 100 : 27 + Time * .38f) * healthFactor,
                speed = (elite ? 45 : 36 + Time * .2f + Rand() * 10) * speedFactor,
                radius = elite ? 28 : 19, type = Rand() < .45f ? "lantern" : "tiger", elite = elite, bob = Rand() * 6.28f });
        }

        private void Fire()
        {
            if (Enemies.Count == 0) return;
            var nearest = new List<CombatActor>(Enemies);
            nearest.Sort((a, b) => Distance(a.x, a.y, PlayerX, PlayerY).CompareTo(Distance(b.x, b.y, PlayerX, PlayerY)));
            for (int i = 0; i < projectileCount; i++)
            {
                var target = nearest[i % nearest.Count];
                float angle = (float)Math.Atan2(target.y - PlayerY, target.x - PlayerX);
                if (i >= nearest.Count) angle += i % 2 == 0 ? -.08f : .08f;
                Projectiles.Add(new SpellShot { id = ++idCounter, x = PlayerX, y = PlayerY - 16,
                    vx = (float)Math.Cos(angle) * 620, vy = (float)Math.Sin(angle) * 620, life = 1.6f, damage = Attack });
            }
        }

        private void Hit(CombatActor enemy, float damage)
        {
            if (enemy.hp <= 0) return;
            Damage += Math.Min(enemy.hp, damage); enemy.hp -= damage; enemy.flash = .1f;
            events.Add(new CombatEvent { type = "hit", x = enemy.x, y = enemy.y, amount = damage });
            if (enemy.hp > 0) return;
            Kills++;
            Drops.Add(new SpiritDrop { id = ++idCounter, x = enemy.x, y = enemy.y, value = enemy.elite ? 4 : 1 });
            events.Add(new CombatEvent { type = "kill", x = enemy.x, y = enemy.y });
        }

        public void Step(float deltaTime, float inputX = 0, float inputY = 0)
        {
            if (Status != "running") return;
            float dt = Clamp(deltaTime, 0, .05f);
            Time = Math.Min(Duration, Time + dt);
            if (Time >= Duration) { Finish(true); return; }
            Invulnerability = Math.Max(0, Invulnerability - dt);
            float length = (float)Math.Sqrt(inputX * inputX + inputY * inputY);
            if (length > 1) { inputX /= length; inputY /= length; }
            PlayerX = Clamp(PlayerX + inputX * Speed * dt, minPlayerX, maxPlayerX);
            PlayerY = Clamp(PlayerY + inputY * Speed * dt, minPlayerY, maxPlayerY);
            if (Math.Abs(inputX) > .05f) Facing = inputX > 0 ? 1 : -1;
            spawnTimer -= dt;
            if (spawnTimer <= 0 && Enemies.Count < 100)
            {
                SpawnEnemy();
                spawnTimer = Math.Max(.28f, .88f - Time * .006f) * (Stage == "moon" ? .8f : Stage == "ruins" ? .9f : 1f);
                if (Time > 50 && Rand() < .35f) SpawnEnemy();
            }
            attackTimer -= dt;
            if (attackTimer <= 0) { Fire(); attackTimer = interval; }
            if (UpgradeLevel("pulse") > 0)
            {
                pulseTimer -= dt;
                if (pulseTimer <= 0)
                {
                    pulseTimer = 3; float range = 175 + UpgradeLevel("pulse") * 18;
                    events.Add(new CombatEvent { type = "pulse", x = PlayerX, y = PlayerY, amount = range });
                    foreach (var enemy in Enemies)
                    {
                        if (Distance(enemy.x, enemy.y, PlayerX, PlayerY) >= range) continue;
                        Hit(enemy, Attack * (.8f + UpgradeLevel("pulse") * .35f));
                        float angle = (float)Math.Atan2(enemy.y - PlayerY, enemy.x - PlayerX);
                        enemy.x = Clamp(enemy.x + (float)Math.Cos(angle) * 55, 20, WorldWidth - 20);
                        enemy.y = Clamp(enemy.y + (float)Math.Sin(angle) * 55, 20, WorldHeight - 20);
                    }
                }
            }
            if (Character == "lingxiu" || UpgradeLevel("mend") > 0)
            {
                healTimer -= dt;
                if (healTimer <= 0) { healTimer = 5; Hp = Math.Min(MaxHp, Hp + 3 + UpgradeLevel("mend") * 4); }
            }
            foreach (var enemy in Enemies)
            {
                if (enemy.hp <= 0) continue;
                enemy.flash = Math.Max(0, enemy.flash - dt);
                float d = Distance(enemy.x, enemy.y, PlayerX, PlayerY);
                float angle = (float)Math.Atan2(PlayerY - enemy.y, PlayerX - enemy.x);
                if (d > 2) { enemy.x += (float)Math.Cos(angle) * enemy.speed * dt; enemy.y += (float)Math.Sin(angle) * enemy.speed * dt; }
                if (d < enemy.radius + 21) { DamagePlayer(enemy.elite ? 18 : 10); if (Status == "ended") return; }
            }
            foreach (var shot in Projectiles)
            {
                shot.x += shot.vx * dt; shot.y += shot.vy * dt; shot.life -= dt;
                foreach (var enemy in Enemies)
                {
                    if (enemy.hp <= 0 || Distance(enemy.x, enemy.y, shot.x, shot.y) >= enemy.radius + 12) continue;
                    Hit(enemy, shot.damage); shot.life = 0; break;
                }
            }
            Projectiles.RemoveAll(p => p.life <= 0); Enemies.RemoveAll(e => e.hp <= 0);
            int collected = 0;
            foreach (var drop in Drops)
            {
                float d = Distance(drop.x, drop.y, PlayerX, PlayerY);
                if (d >= pickupRange) continue;
                float speed = 280 + (pickupRange - d) * 5;
                if (d < 23 || speed * dt >= d) { collected += drop.value; drop.collected = true; continue; }
                float angle = (float)Math.Atan2(PlayerY - drop.y, PlayerX - drop.x);
                drop.x += (float)Math.Cos(angle) * speed * dt; drop.y += (float)Math.Sin(angle) * speed * dt;
            }
            Drops.RemoveAll(d => d.collected);
            if (collected > 0) AddXp(collected);
        }

        public CombatSnapshot Snapshot()
        {
            var upgrades = new List<string>(); foreach (var item in Upgrades) upgrades.Add(item.Key + ":" + item.Value);
            return new CombatSnapshot { time = Time, duration = Duration, hp = Hp, maxHp = MaxHp,
                level = Level, xp = Xp, xpNext = XpNext, kills = Kills, damage = (int)Damage,
                status = Status, character = Character, stage = Stage, upgrades = upgrades.ToArray() };
        }
    }
}
