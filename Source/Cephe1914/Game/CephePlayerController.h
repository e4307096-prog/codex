#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "CephePlayerController.generated.h"

class UCepheInputConfig;

DECLARE_MULTICAST_DELEGATE_OneParam(FOnMenuKey, int32 /*0..5 = F1..F6*/);

UCLASS()
class CEPHE1914_API ACephePlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ACephePlayerController();

	virtual void BeginPlay() override;
	virtual void SetupInputComponent() override;

	/** Eylemleri tembel uretir; kamera pawn'i da buradan alir (sira bagimsiz). */
	UCepheInputConfig* GetInputConfig();

	/** Imlec bir arayuz panelinin ustunde mi (harita secimini engellemek icin). */
	bool IsPointerOverUI() const;

	FOnMenuKey OnMenuKey;

private:
	void OnClick();
	void SetMode(int32 Index);
	void OnMode1() { SetMode(0); }
	void OnMode2() { SetMode(1); }
	void OnMode3() { SetMode(2); }
	void OnMode4() { SetMode(3); }
	void OnPause();
	void OnSpeedUp();
	void OnSpeedDown();
	void OnMenu1() { OnMenuKey.Broadcast(0); }
	void OnMenu2() { OnMenuKey.Broadcast(1); }
	void OnMenu3() { OnMenuKey.Broadcast(2); }
	void OnMenu4() { OnMenuKey.Broadcast(3); }
	void OnMenu5() { OnMenuKey.Broadcast(4); }
	void OnMenu6() { OnMenuKey.Broadcast(5); }

	UPROPERTY() TObjectPtr<UCepheInputConfig> InputConfig;
};
