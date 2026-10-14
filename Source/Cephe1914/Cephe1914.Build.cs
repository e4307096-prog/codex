using UnrealBuildTool;

public class Cephe1914 : ModuleRules
{
	public Cephe1914(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[]
		{
			"Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput",
			"Slate", "SlateCore", "ImageWrapper", "Json", "JsonUtilities",
			"RenderCore", "RHI", "UMG"
		});
	}
}
