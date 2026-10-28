using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace DaoSurvivor.Editor
{
    /// <summary>Reproducible import, bootstrap-scene creation, and Windows validation build.</summary>
    public static class BuildTools
    {
        const string ScenePath = "Assets/DaoSurvivor/Scenes/Bootstrap.unity";

        [MenuItem("道途幸存者/准备工程与启动场景")]
        public static void PrepareProject()
        {
            Directory.CreateDirectory("Assets/DaoSurvivor/Scenes");
            foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { "Assets/DaoSurvivor/Resources" }))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (!(AssetImporter.GetAtPath(path) is TextureImporter importer)) continue;
                importer.textureType = TextureImporterType.Default;
                importer.alphaIsTransparency = true;
                importer.mipmapEnabled = false;
                importer.npotScale = TextureImporterNPOTScale.None;
                importer.maxTextureSize = 4096;
                importer.filterMode = FilterMode.Bilinear;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                importer.SaveAndReimport();
            }
            if (!File.Exists(ScenePath))
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
            }
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            PlayerSettings.companyName = "DaoSurvivor";
            PlayerSettings.productName = "道途幸存者";
            PlayerSettings.defaultScreenWidth = 1920;
            PlayerSettings.defaultScreenHeight = 1080;
            PlayerSettings.resizableWindow = true;
            PlayerSettings.fullScreenMode = FullScreenMode.Windowed;
            PlayerSettings.runInBackground = true;
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Standalone, ScriptingImplementation.Mono2x);
            // Legacy input is deliberately used by this dependency-free project.
            var settings = new SerializedObject(Unsupported.GetSerializedAssetInterfaceSingleton("PlayerSettings"));
            var input = settings.FindProperty("activeInputHandler");
            if (input != null) { input.intValue = 0; settings.ApplyModifiedProperties(); }
            AssetDatabase.SaveAssets();
            Debug.Log("DAO_PREPARE_OK: " + Application.unityVersion + " / " + ScenePath);
        }

        [MenuItem("道途幸存者/验证并构建 Windows 试玩版")]
        public static void VerifyAndBuild()
        {
            PrepareProject();
            Directory.CreateDirectory("Build/Windows");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = "Build/Windows/DaoSurvivors.exe",
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.Development
            });
            Directory.CreateDirectory("docs/verification");
            var record = new VerificationRecord
            {
                verifiedAt = DateTimeOffset.Now.ToString("o"),
                editorVersion = Application.unityVersion,
                result = result.summary.result.ToString(),
                errorCount = result.summary.totalErrors,
                warningCount = result.summary.totalWarnings,
                outputPath = result.summary.outputPath,
                messages = result.steps.SelectMany(step => step.messages).Where(m => m.type == LogType.Error || m.type == LogType.Exception).Select(m => m.content).ToArray()
            };
            File.WriteAllText("docs/verification/unity-build.json", JsonUtility.ToJson(record, true));
            if (result.summary.result != BuildResult.Succeeded)
                throw new InvalidOperationException("Unity build failed: " + result.summary.result);
            Debug.Log("DAO_BUILD_OK: " + result.summary.outputPath);
        }

        [Serializable]
        class VerificationRecord
        {
            public string verifiedAt, editorVersion, result, outputPath;
            public uint errorCount, warningCount;
            public string[] messages;
        }
    }
}
