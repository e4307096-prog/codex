using UnrealBuildTool;
using System.Collections.Generic;

public class Cephe1914Target : TargetRules
{
	public Cephe1914Target(TargetInfo Target) : base(Target)
	{
		Type = TargetType.Game;
		DefaultBuildSettings = BuildSettingsVersion.V5;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		ExtraModuleNames.Add("Cephe1914");
	}
}
