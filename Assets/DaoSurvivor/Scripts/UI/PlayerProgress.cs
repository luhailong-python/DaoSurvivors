using System;
using UnityEngine;

namespace DaoSurvivor
{
    [Serializable]
    internal sealed class PlayerProgress
    {
        private const string SaveKey = "DaoSurvivors.v1.profile";
        public int version = 1;
        public int coins = 120;
        public int attackLevel, healthLevel, speedLevel;
        public int bestKills, completedRuns, wins;
        public float bestTime;
        public bool sound = true, effects = true;

        internal static PlayerProgress Load()
        {
            if (!PlayerPrefs.HasKey(SaveKey)) return new PlayerProgress();
            try
            {
                var data = JsonUtility.FromJson<PlayerProgress>(PlayerPrefs.GetString(SaveKey));
                if (data == null || data.version != 1) return new PlayerProgress();
                data.coins = Mathf.Clamp(data.coins, 0, 100000000);
                data.attackLevel = Mathf.Clamp(data.attackLevel, 0, 5);
                data.healthLevel = Mathf.Clamp(data.healthLevel, 0, 5);
                data.speedLevel = Mathf.Clamp(data.speedLevel, 0, 5);
                data.bestKills = Mathf.Max(0, data.bestKills); data.completedRuns = Mathf.Max(0, data.completedRuns);
                data.wins = Mathf.Clamp(data.wins, 0, data.completedRuns); data.bestTime = Mathf.Clamp(data.bestTime, 0, 90);
                return data;
            }
            catch (Exception ex)
            {
                Debug.LogWarning("DaoSurvivors local profile could not be read: " + ex.GetType().Name);
                return new PlayerProgress();
            }
        }

        internal void Save() { PlayerPrefs.SetString(SaveKey, JsonUtility.ToJson(this)); PlayerPrefs.Save(); }
        internal int LevelOf(string id) { return id == "attack" ? attackLevel : id == "health" ? healthLevel : speedLevel; }
        internal int CostOf(string id) { return 40 + LevelOf(id) * 25; }
        internal bool TryTrain(string id)
        {
            if (id != "attack" && id != "health" && id != "speed") return false;
            int cost = CostOf(id); if (LevelOf(id) >= 5 || coins < cost) return false;
            coins -= cost;
            if (id == "attack") attackLevel++; else if (id == "health") healthLevel++; else speedLevel++;
            Save(); return true;
        }
    }
}
