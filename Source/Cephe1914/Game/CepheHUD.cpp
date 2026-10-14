#include "Game/CepheHUD.h"
#include "UI/SCepheHUD.h"
#include "Game/CepheClock.h"
#include "Game/CephePlayerController.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "Widgets/SWeakWidget.h"

namespace
{
	const TCHAR* MenuNames[6] = { TEXT("DİPLOMASİ"), TEXT("EKONOMİ"), TEXT("ORDU"), TEXT("TEKNOLOJİ"), TEXT("SİYASET"), TEXT("KARARLAR") };
	const TCHAR* LayerNames[4] = { TEXT("SİYASİ"), TEXT("İTTİFAK"), TEXT("CEPHE"), TEXT("ARAZİ") };
	const TCHAR* Dispatches[] =
	{
		TEXT("PARİS STOP İPRES ÇEVRESİNDE TOPÇU ATEŞİ ARTTI STOP"),
		TEXT("BERLİN STOP KUZEY KANATTA YENİ TÜMENLER YOLDA STOP"),
		TEXT("PETROGRAD STOP GALİÇYA CEPHESİNDE İLERLEYİŞ SÜRÜYOR STOP"),
		TEXT("LONDRA STOP ÖRTÜLÜ MÜHİMMAT SEVKİYATI LİMANA ULAŞTI STOP"),
		TEXT("VİYANA STOP KARPATLARDA KAR BASTIRDI STOP"),
		TEXT("BRÜKSEL STOP İŞGAL İDARESİ YENİ FERMAN YAYIMLADI STOP"),
	};
}

void ACepheHUD::BeginPlay()
{
	Super::BeginPlay();
	if (!GEngine || !GEngine->GameViewport || !GetWorld()) return;

	UProvinceMapSubsystem* Map = GetWorld()->GetSubsystem<UProvinceMapSubsystem>();
	UCepheClock* Clock = GetWorld()->GetSubsystem<UCepheClock>();
	ACephePlayerController* PC = Cast<ACephePlayerController>(PlayerOwner);
	if (Map) Map->EnsureLoaded();

	Widget = SNew(SCepheHUD).Map(Map).Clock(Clock).Controller(PC).PlayerNation(PlayerNation);
	Container = SNew(SWeakWidget).PossiblyNullContent(Widget.ToSharedRef());
	GEngine->GameViewport->AddViewportWidgetContent(Container.ToSharedRef(), 10);

	if (Map)
	{
		Map->OnProvinceSelected.AddUObject(this, &ACepheHUD::HandleSelectionChanged);
		Map->OnArmySelected.AddUObject(this, &ACepheHUD::HandleSelectionChanged);
		Map->OnMapModeChanged.AddUObject(this, &ACepheHUD::HandleMapMode);
	}
	if (Clock) Clock->OnDayChanged.AddUObject(this, &ACepheHUD::HandleDay);
	if (PC) PC->OnMenuKey.AddUObject(this, &ACepheHUD::HandleMenu);

	PushTelegram(TEXT("14 KASIM 1914 STOP BATI CEPHESİ DURGUN FAKAT GERGİN STOP"));
}

void ACepheHUD::EndPlay(const EEndPlayReason::Type Reason)
{
	if (UWorld* W = GetWorld())
	{
		if (UProvinceMapSubsystem* Map = W->GetSubsystem<UProvinceMapSubsystem>())
		{
			Map->OnProvinceSelected.RemoveAll(this);
			Map->OnArmySelected.RemoveAll(this);
			Map->OnMapModeChanged.RemoveAll(this);
		}
		if (UCepheClock* Clock = W->GetSubsystem<UCepheClock>()) Clock->OnDayChanged.RemoveAll(this);
	}
	if (ACephePlayerController* PC = Cast<ACephePlayerController>(PlayerOwner)) PC->OnMenuKey.RemoveAll(this);

	if (Container.IsValid() && GEngine && GEngine->GameViewport)
	{
		GEngine->GameViewport->RemoveViewportWidgetContent(Container.ToSharedRef());
	}
	Container.Reset();
	Widget.Reset();
	Super::EndPlay(Reason);
}

bool ACepheHUD::IsPointerOverUI() const
{
	return Widget.IsValid() && Widget->IsPointerOverUI();
}

void ACepheHUD::PushTelegram(const FString& Text)
{
	if (Widget.IsValid()) Widget->PushTelegram(Text);
}

void ACepheHUD::HandleSelectionChanged(int32)
{
	if (Widget.IsValid()) Widget->RefreshSelection();
}

void ACepheHUD::HandleMapMode(EMapMode Mode)
{
	PushTelegram(FString::Printf(TEXT("HARİTA KATMANI %s STOP"), LayerNames[FMath::Clamp(static_cast<int32>(Mode), 0, 3)]));
}

void ACepheHUD::HandleMenu(int32 Index)
{
	if (!Widget.IsValid()) return;
	Index = FMath::Clamp(Index, 0, 5);
	Widget->SetActiveMenu(Index);
	PushTelegram(FString::Printf(TEXT("%s DAİRESİ HENÜZ AÇILMADI STOP"), MenuNames[Index]));
}

void ACepheHUD::HandleDay(const FDateTime&)
{
	PushTelegram(Dispatches[TelegramCursor++ % UE_ARRAY_COUNT(Dispatches)]);
}
