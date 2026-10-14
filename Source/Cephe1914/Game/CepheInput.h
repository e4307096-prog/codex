#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "CepheInput.generated.h"

class UInputAction;
class UInputMappingContext;

/** Enhanced Input eylemleri ve eslemesi: asset olmadan C++'ta uretilir. */
UCLASS()
class CEPHE1914_API UCepheInputConfig : public UObject
{
	GENERATED_BODY()

public:
	void Build();

	UPROPERTY() TObjectPtr<UInputMappingContext> Context;
	UPROPERTY() TObjectPtr<UInputAction> Click;
	UPROPERTY() TObjectPtr<UInputAction> Move;     // Axis2D: X sag, Y ileri
	UPROPERTY() TObjectPtr<UInputAction> Zoom;     // Axis1D: fare tekerlegi
	UPROPERTY() TObjectPtr<UInputAction> Rotate;   // Axis1D: Q -1, E +1
	UPROPERTY() TObjectPtr<UInputAction> Pause;
	UPROPERTY() TObjectPtr<UInputAction> SpeedUp;
	UPROPERTY() TObjectPtr<UInputAction> SpeedDown;
	UPROPERTY() TObjectPtr<UInputAction> Mode1;
	UPROPERTY() TObjectPtr<UInputAction> Mode2;
	UPROPERTY() TObjectPtr<UInputAction> Mode3;
	UPROPERTY() TObjectPtr<UInputAction> Mode4;
	UPROPERTY() TObjectPtr<UInputAction> Menu1;
	UPROPERTY() TObjectPtr<UInputAction> Menu2;
	UPROPERTY() TObjectPtr<UInputAction> Menu3;
	UPROPERTY() TObjectPtr<UInputAction> Menu4;
	UPROPERTY() TObjectPtr<UInputAction> Menu5;
	UPROPERTY() TObjectPtr<UInputAction> Menu6;

private:
	bool bBuilt = false;
};
