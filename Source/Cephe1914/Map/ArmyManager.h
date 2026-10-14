#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ArmyManager.generated.h"

class AArmyCounterActor;

/** armies.json'daki her ordu icin AArmyCounterActor uretir (GameMode BeginPlay'de olusturulur). */
UCLASS()
class CEPHE1914_API AArmyManager : public AActor
{
	GENERATED_BODY()

public:
	AArmyManager();
	virtual void BeginPlay() override;

	UPROPERTY(EditAnywhere, Category = "Cephe") float ZOffset = 80.f;
	UPROPERTY(EditAnywhere, Category = "Cephe") float CounterScale = 1.f;
	/** Ayni bolgedeki ordular arasi yanal aralik (cm). */
	UPROPERTY(EditAnywhere, Category = "Cephe") float StackSpacing = 450.f;

	UPROPERTY() TArray<TObjectPtr<AArmyCounterActor>> Counters;
};
