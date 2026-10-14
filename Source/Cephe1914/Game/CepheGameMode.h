#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "CepheGameMode.generated.h"

UCLASS()
class CEPHE1914_API ACepheGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ACepheGameMode();
	virtual void BeginPlay() override;

private:
	template <class T>
	void SpawnIfMissing();
};
