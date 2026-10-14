#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/DeclarativeSyntaxSupport.h"
#include "Brushes/SlateColorBrush.h"

class UProvinceMapSubsystem;
class UCepheClock;
class ACephePlayerController;
struct FProvinceRow;
struct FArmyRecord;
class SBox;
class SVerticalBox;

/** Tamamen C++ Slate arayuzu: harita masasi (kagit, murekkep cerceve, daktilo yazisi) estetigi. */
class CEPHE1914_API SCepheHUD : public SCompoundWidget
{
public:
	SLATE_BEGIN_ARGS(SCepheHUD) {}
		SLATE_ARGUMENT(TWeakObjectPtr<UProvinceMapSubsystem>, Map)
		SLATE_ARGUMENT(TWeakObjectPtr<UCepheClock>, Clock)
		SLATE_ARGUMENT(TWeakObjectPtr<ACephePlayerController>, Controller)
		SLATE_ARGUMENT(FString, PlayerNation)
	SLATE_END_ARGS()

	void Construct(const FArguments& InArgs);

	void RefreshSelection();
	void PushTelegram(const FString& Text);
	void SetActiveMenu(int32 Index) { ActiveMenu = Index; }
	bool IsPointerOverUI() const;

private:
	TSharedRef<SWidget> Panel(const TSharedRef<SWidget>& Content, const FMargin& Pad);
	TSharedRef<SWidget> MakeButton(const FString& Label, TFunction<void()> OnClick, TFunction<bool()> IsActive, int32 FontSize);
	TSharedRef<SWidget> Row(const FString& Label, const FString& Value) const;
	TSharedRef<SWidget> Bar(float Fraction, const FLinearColor& Fill, float Width) const;
	TSharedRef<SWidget> Flag() const;

	TSharedRef<SWidget> BuildTopBar();
	TSharedRef<SWidget> BuildLeftMenu();
	TSharedRef<SWidget> BuildTelegraph();
	TSharedRef<SWidget> BuildSelection();
	TSharedRef<SWidget> BuildLayers();
	TSharedRef<SWidget> BuildSelectionContent();
	TSharedRef<SWidget> BuildProvince(const FProvinceRow& P);
	TSharedRef<SWidget> BuildArmy(const FArmyRecord& A);
	TSharedRef<SWidget> Resource(const FString& Label, const FString& Value) const;

	FString NationName(const FString& Code) const;

	TWeakObjectPtr<UProvinceMapSubsystem> Map;
	TWeakObjectPtr<UCepheClock> Clock;
	TWeakObjectPtr<ACephePlayerController> Controller;
	FString PlayerNation;

	FSlateColorBrush WhiteBrush = FSlateColorBrush(FLinearColor::White);
	TSharedPtr<SBox> SelectionBox;
	TSharedPtr<SVerticalBox> TelegraphList;
	TArray<TSharedPtr<SWidget>> HoverPanels;
	TArray<FString> Telegrams;
	int32 ActiveMenu = -1;
};
