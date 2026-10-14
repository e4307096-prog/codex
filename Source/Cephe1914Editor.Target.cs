using UnrealBuildTool;
using System.Collections.Generic;

public class Cephe1914EditorTarget : TargetRules
{
	public Cephe1914EditorTarget(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Editor;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("Cephe1914");
	}
}
