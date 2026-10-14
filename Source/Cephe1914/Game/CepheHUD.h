#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "Core/CepheTypes.h"
#include "Misc/DateTime.h"
#include "CepheHUD.generated.h"

class SCepheHUD;
class SWidget;

/** Slate arayuzunu viewport'a ekler ve alt sistem/saat/denetleyici olaylarina baglar. */
UCLASS()
class CEPHE1914_API ACepheHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

	bool IsPointerOverUI() const;
	void PushTelegram(const FString& Text);

	UPROPERTY(EditAnywhere, Category = "Cephe") FString PlayerNation = TEXT("FRA");

private:
	void HandleSelectionChanged(int32 Id);
	void HandleMapMode(EMapMode Mode);
	void HandleMenu(int32 Index);
	void HandleDay(const FDateTime& Date);

	TSharedPtr<SCepheHUD> Widget;
	TSharedPtr<SWidget> Container;
	int32 TelegramCursor = 0;
};
