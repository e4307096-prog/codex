#include "Game/CepheGameMode.h"
#include "Game/CephePlayerController.h"
#include "Game/CepheHUD.h"
#include "Camera/StrategyCameraPawn.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Map/ProvinceMapActor.h"
#include "Map/FrontLineActor.h"
#include "Map/RailNetworkActor.h"
#include "Map/ArmyManager.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ACepheGameMode::ACepheGameMode()
{
	DefaultPawnClass = AStrategyCameraPawn::StaticClass();
	PlayerControllerClass = ACephePlayerController::StaticClass();
	HUDClass = ACepheHUD::StaticClass();
}

template <class T>
void ACepheGameMode::SpawnIfMissing()
{
	UWorld* World = GetWorld();
	for (TActorIterator<T> It(World); It; ++It)
	{
		return; // haritada zaten var (level betigi yerlestirmis)
	}
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	World->SpawnActor<T>(FVector::ZeroVector, FRotator::ZeroRotator, Params);
}

void ACepheGameMode::BeginPlay()
{
	if (UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>())
	{
		Map->EnsureLoaded();
	}
	SpawnIfMissing<AProvinceMapActor>();
	SpawnIfMissing<AFrontLineActor>();
	SpawnIfMissing<ARailNetworkActor>();
	SpawnIfMissing<AArmyManager>();
	Super::BeginPlay();
}
