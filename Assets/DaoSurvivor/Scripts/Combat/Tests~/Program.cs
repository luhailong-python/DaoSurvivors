using System;
using System.Linq;
using DaoSurvivor;

internal static class Program
{
    private static int checks;
    private static void Check(bool condition, string name)
    {
        if (!condition) throw new Exception("FAILED: " + name);
        checks++; Console.WriteLine("PASS " + name);
    }
    private static void Advance(RunModel model, float seconds, float dx = 0, float dy = 0)
    {
        int frames = (int)Math.Ceiling(seconds / .02f);
        for (int i = 0; i < frames; i++) model.Step(.02f, dx, dy);
    }
    public static void Main()
    {
        var model = new RunModel(7); model.Begin("qingyun", "bamboo");
        Check(model.Hp == 120 && model.Status == "running" && model.Duration == 90, "new run has expected initial state");
        model.SetPaused(true); Advance(model, 1, 1);
        Check(model.Time == 0 && model.PlayerX == 900, "pause freezes movement and timer");
        model.SetPaused(false); Advance(model, 1, 1);
        Check(model.Time > .99f && model.PlayerX > 1100, "resume advances simulation and input");

        var diagonal = new RunModel(7); diagonal.Begin("qingyun", "bamboo"); Advance(diagonal, 1, 1, 1);
        float diagonalDistance = (float)Math.Sqrt(Math.Pow(diagonal.PlayerX - 900, 2) + Math.Pow(diagonal.PlayerY - 575, 2));
        Check(Math.Abs(diagonalDistance - 205) < .1f, "diagonal movement has no speed advantage");
        diagonal.SetPlayerBounds(30, 270, 1770, 1070); Advance(diagonal, 5, 0, -1);
        Check(diagonal.PlayerY == 270, "player stays below reserved top HUD and sprite head extent");
        Advance(diagonal, 10, 0, 1);
        Check(diagonal.PlayerY == 1070, "player stays above bottom HUD and sprite foot extent");

        model.Begin("qingyun", "bamboo"); model.AddXp(6);
        Check(model.Status == "upgrade" && model.Level == 2 && model.Choices.Length == 3 && model.Choices.Select(c => c.id).Distinct().Count() == 3,
            "EXP produces three distinct upgrade choices");
        Check(!model.ChooseUpgrade("invalid") && model.Status == "upgrade", "invalid upgrade cannot resume run");
        string selected = model.Choices[0].id;
        Check(model.ChooseUpgrade(selected) && model.Upgrades[selected] == 1 && model.Status == "running", "selected upgrade applies once and resumes");
        Check(!model.ChooseUpgrade(selected) && model.Upgrades[selected] == 1, "duplicate selection is ignored");

        model.Begin("qingyun", "bamboo"); model.AddXp(30); int choices = 0;
        while (model.Status == "upgrade") { choices++; model.ChooseUpgrade(model.Choices[0].id); }
        Check(choices == 3 && model.Level == 4 && model.Xp == 0, "surplus EXP survives chained level-ups");

        model.Begin("jianxiu", "moon", 2, 3, 2);
        Check(model.Hp == 130 && Math.Abs(model.Attack - 24.2f) < .001f && Math.Abs(model.Speed - 233.2f) < .01f,
            "character and permanent bonuses affect actual combat values");
        model.DamagePlayer(25); model.DamagePlayer(25);
        Check(model.Hp == 105, "contact invulnerability prevents repeated damage in one frame");
        Advance(model, .8f); model.DamagePlayer(9999);
        Check(model.Status == "ended" && !model.Result.victory, "lethal damage ends run");
        Advance(model, 2); model.DamagePlayer(9999);
        Check(model.TakeEvents().Count(e => e.type == "end") == 1, "defeat emits exactly one settlement event");

        model.Begin("qingyun", "bamboo", duration: 1); Advance(model, 2);
        Check(model.Result.victory && model.Time == 1 && model.Result.coins >= 100, "duration completion produces victory rewards");
        Advance(model, 2); Check(model.TakeEvents().Count(e => e.type == "end") == 1, "victory emits exactly one settlement event");

        model.Begin("qingyun", "bamboo");
        model.Enemies.Add(new CombatActor { id = 7000, x = 930, y = 575, hp = 10, speed = 0, radius = 20 });
        Advance(model, .8f);
        Check(model.Kills >= 1 && model.Damage >= 10, "automatic spell collides and defeats an enemy");
        Check(model.Xp > 0, "defeated enemy drops collectable EXP");

        model.AddXp(100); model.Stop();
        Check(model.Status == "idle" && model.Choices.Length == 0 && model.TakeEvents().Length == 0, "abandon clears pending callbacks and choices");
        model.Begin("lingxiu", "ruins");
        Check(model.Time == 0 && model.Kills == 0 && model.Enemies.Count == 0 && model.Upgrades.Count == 0 && model.Hp == 150,
            "restarting never inherits prior run state");
        Console.WriteLine("Combat checks passed: " + checks);
    }
}
