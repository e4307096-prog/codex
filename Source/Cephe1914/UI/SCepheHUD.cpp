#include "UI/SCepheHUD.h"
#include "Map/ProvinceMapSubsystem.h"
#include "Game/CepheClock.h"
#include "Game/CephePlayerController.h"
#include "Core/CepheTypes.h"
#include "Core/CepheData.h"
#include "Misc/Paths.h"
#include "Styling/CoreStyle.h"
#include "Fonts/SlateFontInfo.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SNullWidget.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SSpacer.h"
#include "Widgets/Text/STextBlock.h"
#include "Input/Events.h"
#include "InputCoreTypes.h"

namespace
{
	FLinearColor S(int32 R, int32 G, int32 B)
	{
		return FLinearColor::FromSRGBColor(FColor(R, G, B));
	}
	const FLinearColor Paper = FLinearColor::FromSRGBColor(FColor(226, 212, 176));
	const FLinearColor PaperDark = FLinearColor::FromSRGBColor(FColor(196, 178, 138));
	const FLinearColor Ink = FLinearColor::FromSRGBColor(FColor(28, 22, 16));
	const FLinearColor InkSoft = FLinearColor::FromSRGBColor(FColor(90, 76, 56));
	const FLinearColor Active = FLinearColor::FromSRGBColor(FColor(214, 150, 90));
	const FLinearColor RedInk = FLinearColor::FromSRGBColor(FColor(140, 32, 24));

	FSlateFontInfo Mono(int32 Size)
	{
		static const FString Path = FPaths::Combine(FPaths::EngineContentDir(), TEXT("Slate/Fonts/DroidSansMono.ttf"));
		static const bool bHas = FPaths::FileExists(Path);
		if (bHas) return FSlateFontInfo(Path, Size);
		return FCoreStyle::GetDefaultFontStyle("Regular", Size);
	}
	FSlateFontInfo Bold(int32 Size)
	{
		return FCoreStyle::GetDefaultFontStyle("Bold", Size);
	}

	const TCHAR* Months[12] = { TEXT("Ocak"), TEXT("Şubat"), TEXT("Mart"), TEXT("Nisan"), TEXT("Mayıs"), TEXT("Haziran"),
	                            TEXT("Temmuz"), TEXT("Ağustos"), TEXT("Eylül"), TEXT("Ekim"), TEXT("Kasım"), TEXT("Aralık") };
	const TCHAR* MenuNames[6] = { TEXT("Diplomasi"), TEXT("Ekonomi"), TEXT("Ordu"), TEXT("Teknoloji"), TEXT("Siyaset"), TEXT("Kararlar") };
	const TCHAR* LayerNames[4] = { TEXT("Siyasi"), TEXT("İttifak"), TEXT("Cephe"), TEXT("Arazi") };
	const TCHAR* TerrainNames[5] = { TEXT("Ova"), TEXT("Orman"), TEXT("Tepelik"), TEXT("Dağlık"), TEXT("Bataklık") };
	const TCHAR* SideNames[3] = { TEXT("Tarafsız"), TEXT("İtilaf"), TEXT("İttifak") };

	void FlagColors(const FString& Code, const FLinearColor& Fallback, FLinearColor Out[3])
	{
		auto Set = [&](FColor A, FColor B, FColor C)
		{
			Out[0] = FLinearColor::FromSRGBColor(A);
			Out[1] = FLinearColor::FromSRGBColor(B);
			Out[2] = FLinearColor::FromSRGBColor(C);
		};
		const FColor Red(190, 40, 40), White(240, 236, 224), Blue(40, 70, 150), Black(30, 30, 30);
		if (Code == TEXT("FRA")) Set(Blue, White, Red);
		else if (Code == TEXT("GER")) Set(Black, White, Red);
		else if (Code == TEXT("RUS")) Set(White, Blue, Red);
		else if (Code == TEXT("BEL")) Set(Black, FColor(240, 200, 40), Red);
		else if (Code == TEXT("ITA")) Set(FColor(40, 130, 60), White, Red);
		else Out[0] = Out[1] = Out[2] = Fallback;
	}

}

TSharedRef<SWidget> SCepheHUD::Panel(const TSharedRef<SWidget>& Content, const FMargin& Pad)
{
	TSharedRef<SWidget> Outer =
		SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Ink)).Padding(FMargin(2.f))
		[
			SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(PaperDark)).Padding(FMargin(1.f))
			[
				SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Paper)).Padding(Pad)
				[
					Content
				]
			]
		];
	HoverPanels.Add(Outer);
	return Outer;
}

TSharedRef<SWidget> SCepheHUD::MakeButton(const FString& Label, TFunction<void()> OnClick, TFunction<bool()> IsActive, int32 FontSize)
{
	return SNew(SBorder)
		.BorderImage(&WhiteBrush)
		.BorderBackgroundColor_Lambda([IsActive]() -> FSlateColor
		{
			return FSlateColor((IsActive && IsActive()) ? Active : PaperDark);
		})
		.Padding(FMargin(8.f, 3.f))
		.OnMouseButtonDown_Lambda([OnClick](const FGeometry&, const FPointerEvent& E) -> FReply
		{
			if (E.GetEffectingButton() == EKeys::LeftMouseButton)
			{
				if (OnClick) OnClick();
				return FReply::Handled();
			}
			return FReply::Unhandled();
		})
		[
			SNew(STextBlock).Text(FText::FromString(Label)).Font(Mono(FontSize)).ColorAndOpacity(FSlateColor(Ink))
		];
}

TSharedRef<SWidget> SCepheHUD::Row(const FString& Label, const FString& Value) const
{
	return SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 1.f, 8.f, 1.f))
		[
			SNew(SBox).WidthOverride(84.f)
			[
				SNew(STextBlock).Text(FText::FromString(Label)).Font(Bold(10)).ColorAndOpacity(FSlateColor(InkSoft))
			]
		]
		+ SHorizontalBox::Slot().FillWidth(1.f).Padding(FMargin(0.f, 1.f))
		[
			SNew(STextBlock).Text(FText::FromString(Value)).Font(Mono(12)).ColorAndOpacity(FSlateColor(Ink))
		];
}

TSharedRef<SWidget> SCepheHUD::Bar(float Fraction, const FLinearColor& Fill, float Width) const
{
	Fraction = FMath::Clamp(Fraction, 0.f, 1.f);
	return SNew(SBox).WidthOverride(Width).HeightOverride(12.f)
	[
		SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Ink)).Padding(FMargin(1.f))
		[
			SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(PaperDark)).Padding(FMargin(0.f))
			[
				SNew(SHorizontalBox)
				+ SHorizontalBox::Slot().FillWidth(FMath::Max(Fraction, 0.0001f))
				[
					SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Fill))
				]
				+ SHorizontalBox::Slot().FillWidth(FMath::Max(1.f - Fraction, 0.0001f))
				[
					SNullWidget::NullWidget
				]
			]
		]
	];
}

TSharedRef<SWidget> SCepheHUD::Flag() const
{
	FLinearColor C[3];
	const FLinearColor Fallback = Map.IsValid() ? Map->GetNationColor(PlayerNation) : FLinearColor::Gray;
	FlagColors(PlayerNation, Fallback, C);
	auto Stripe = [&](const FLinearColor& Col)
	{
		return SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Col)).Padding(FMargin(0.f))
			[ SNew(SSpacer).Size(FVector2D(12.0, 24.0)) ];
	};
	return SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Ink)).Padding(FMargin(2.f))
	[
		SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().AutoWidth()[ Stripe(C[0]) ]
		+ SHorizontalBox::Slot().AutoWidth()[ Stripe(C[1]) ]
		+ SHorizontalBox::Slot().AutoWidth()[ Stripe(C[2]) ]
	];
}

FString SCepheHUD::NationName(const FString& Code) const
{
	if (Map.IsValid())
	{
		if (const FNationRow* N = Map->FindNation(Code)) return N->Name;
	}
	return Code;
}

TSharedRef<SWidget> SCepheHUD::Resource(const FString& Label, const FString& Value) const
{
	return SNew(SVerticalBox)
		+ SVerticalBox::Slot().AutoHeight()
		[
			SNew(STextBlock).Text(FText::FromString(Label)).Font(Bold(8)).ColorAndOpacity(FSlateColor(InkSoft))
		]
		+ SVerticalBox::Slot().AutoHeight()
		[
			SNew(STextBlock).Text(FText::FromString(Value)).Font(Mono(13)).ColorAndOpacity(FSlateColor(Ink))
		];
}

TSharedRef<SWidget> SCepheHUD::BuildTopBar()
{
	TSharedRef<SHorizontalBox> Speed = SNew(SHorizontalBox);
	for (int32 i = 0; i <= 4; ++i)
	{
		TWeakObjectPtr<UCepheClock> C = Clock;
		Speed->AddSlot().AutoWidth().Padding(FMargin(2.f, 0.f))
		[
			MakeButton(i == 0 ? TEXT("II") : FString::FromInt(i),
				[C, i]() { if (C.IsValid()) { if (i == 0) C->TogglePause(); else C->SetSpeed(i); } },
				[C, i]() { return C.IsValid() && C->GetSpeed() == i; }, 12)
		];
	}

	// Kaynak degerleri yer tutucudur (ekonomi sistemi henuz yok).
	return Panel(
		SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(FMargin(0.f, 0.f, 10.f, 0.f))[ Flag() ]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(FMargin(0.f, 0.f, 24.f, 0.f))
		[
			SNew(STextBlock).Text(FText::FromString(NationName(PlayerNation).ToUpper())).Font(Bold(18)).ColorAndOpacity(FSlateColor(Ink))
		]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 0.f, 18.f, 0.f))[ Resource(TEXT("İNSAN GÜCÜ"), TEXT("1,2 Mn")) ]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 0.f, 18.f, 0.f))[ Resource(TEXT("SANAYİ"), TEXT("64")) ]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 0.f, 18.f, 0.f))[ Resource(TEXT("CEPHANE"), TEXT("420")) ]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 0.f, 18.f, 0.f))[ Resource(TEXT("HAZİNE"), TEXT("3,4 Mn")) ]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(0.f, 0.f, 18.f, 0.f))[ Resource(TEXT("SAVAŞ DESTEĞİ"), TEXT("%71")) ]
		+ SHorizontalBox::Slot().FillWidth(1.f)[ SNew(SSpacer) ]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(FMargin(0.f, 0.f, 16.f, 0.f))
		[
			SNew(STextBlock)
			.Text_Lambda([this]()
			{
				if (!Clock.IsValid()) return FText::GetEmpty();
				const FDateTime D = Clock->GetDate();
				return FText::FromString(FString::Printf(TEXT("%d %s %d  %02d:00"), D.GetDay(), Months[D.GetMonth() - 1], D.GetYear(), D.GetHour()));
			})
			.Font(Mono(15)).ColorAndOpacity(FSlateColor(Ink))
		]
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[ Speed ],
		FMargin(10.f, 6.f));
}

TSharedRef<SWidget> SCepheHUD::BuildLeftMenu()
{
	TSharedRef<SVerticalBox> Box = SNew(SVerticalBox);
	Box->AddSlot().AutoHeight().Padding(FMargin(0.f, 0.f, 0.f, 4.f))
	[
		SNew(STextBlock).Text(FText::FromString(TEXT("DAİRELER"))).Font(Bold(11)).ColorAndOpacity(FSlateColor(RedInk))
	];
	for (int32 i = 0; i < 6; ++i)
	{
		TWeakObjectPtr<ACephePlayerController> PC = Controller;
		const FString Label = FString::Printf(TEXT("F%d  %s"), i + 1, MenuNames[i]);
		Box->AddSlot().AutoHeight().Padding(FMargin(0.f, 2.f))
		[
			SNew(SBox).WidthOverride(150.f)
			[
				MakeButton(Label,
					[PC, i]() { if (PC.IsValid()) PC->OnMenuKey.Broadcast(i); },
					[this, i]() { return ActiveMenu == i; }, 12)
			]
		];
	}
	return Panel(Box, FMargin(8.f));
}

TSharedRef<SWidget> SCepheHUD::BuildTelegraph()
{
	SAssignNew(TelegraphList, SVerticalBox);
	return Panel(
		SNew(SBox).WidthOverride(330.f)
		[
			SNew(SVerticalBox)
			+ SVerticalBox::Slot().AutoHeight().Padding(FMargin(0.f, 0.f, 0.f, 4.f))
			[
				SNew(STextBlock).Text(FText::FromString(TEXT("TELGRAF"))).Font(Bold(11)).ColorAndOpacity(FSlateColor(RedInk))
			]
			+ SVerticalBox::Slot().AutoHeight()[ TelegraphList.ToSharedRef() ]
		],
		FMargin(8.f));
}

void SCepheHUD::PushTelegram(const FString& Text)
{
	Telegrams.Add(Text);
	while (Telegrams.Num() > 5) Telegrams.RemoveAt(0);
	if (!TelegraphList.IsValid()) return;

	TelegraphList->ClearChildren();
	for (int32 i = Telegrams.Num() - 1; i >= 0; --i)
	{
		TelegraphList->AddSlot().AutoHeight().Padding(FMargin(0.f, 3.f))
		[
			SNew(STextBlock).Text(FText::FromString(Telegrams[i])).Font(Mono(10)).AutoWrapText(true)
			.ColorAndOpacity(FSlateColor(i == Telegrams.Num() - 1 ? Ink : InkSoft))
		];
	}
}

TSharedRef<SWidget> SCepheHUD::BuildSelection()
{
	SAssignNew(SelectionBox, SBox).MinDesiredWidth(360.f).MaxDesiredWidth(360.f);
	SelectionBox->SetContent(BuildSelectionContent());
	return Panel(SelectionBox.ToSharedRef(), FMargin(10.f, 8.f));
}

void SCepheHUD::RefreshSelection()
{
	if (SelectionBox.IsValid())
	{
		SelectionBox->SetContent(BuildSelectionContent());
	}
}

TSharedRef<SWidget> SCepheHUD::BuildSelectionContent()
{
	UProvinceMapSubsystem* M = Map.Get();
	if (M)
	{
		const int32 ArmyIdx = M->GetSelectedArmy();
		if (ArmyIdx >= 0 && M->GetArmies().IsValidIndex(ArmyIdx))
		{
			return BuildArmy(M->GetArmies()[ArmyIdx]);
		}
		if (const FProvinceRow* P = M->FindProvince(M->GetSelectedProvince()))
		{
			return BuildProvince(*P);
		}
	}
	return SNew(SVerticalBox)
		+ SVerticalBox::Slot().AutoHeight()
		[
			SNew(STextBlock).Text(FText::FromString(TEXT("SEÇİM YOK"))).Font(Bold(13)).ColorAndOpacity(FSlateColor(Ink))
		]
		+ SVerticalBox::Slot().AutoHeight().Padding(FMargin(0.f, 4.f, 0.f, 0.f))
		[
			SNew(STextBlock).Text(FText::FromString(TEXT("Haritada bir bölgeye veya orduya tıklayın."))).Font(Mono(11))
			.AutoWrapText(true).ColorAndOpacity(FSlateColor(InkSoft))
		];
}

TSharedRef<SWidget> SCepheHUD::BuildProvince(const FProvinceRow& P)
{
	const int32 Trench = Map.IsValid() ? Map->GetTrenchLevel(P.Id) : 0;
	const ESide Side = Map.IsValid() ? Map->GetSideOfNation(P.Controller) : ESide::Neutral;

	TSharedRef<SHorizontalBox> Boxes = SNew(SHorizontalBox);
	for (int32 i = 0; i < 5; ++i)
	{
		Boxes->AddSlot().AutoWidth().Padding(FMargin(0.f, 0.f, 3.f, 0.f))
		[
			SNew(SBorder).BorderImage(&WhiteBrush).BorderBackgroundColor(FSlateColor(Ink)).Padding(FMargin(1.f))
			[
				SNew(SBorder).BorderImage(&WhiteBrush)
				.BorderBackgroundColor(FSlateColor(i < Trench ? RedInk : PaperDark))
				[
					SNew(SSpacer).Size(FVector2D(14.0, 14.0))
				]
			]
		];
	}

	return SNew(SVerticalBox)
		+ SVerticalBox::Slot().AutoHeight().Padding(FMargin(0.f, 0.f, 0.f, 6.f))
		[
			SNew(STextBlock).Text(FText::FromString(P.Name.ToUpper())).Font(Bold(16)).ColorAndOpacity(FSlateColor(Ink))
		]
		+ SVerticalBox::Slot().AutoHeight()[ Row(TEXT("SAHİP"), NationName(P.Owner)) ]
		+ SVerticalBox::Slot().AutoHeight()[ Row(TEXT("KONTROL"), NationName(P.Controller)) ]
		+ SVerticalBox::Slot().AutoHeight()[ Row(TEXT("TARAF"), SideNames[static_cast<int32>(Side)]) ]
		+ SVerticalBox::Slot().AutoHeight()[ Row(TEXT("ARAZİ"), TerrainNames[FMath::Clamp(static_cast<int32>(P.Terrain), 0, 4)]) ]
		+ SVerticalBox::Slot().AutoHeight()[ Row(TEXT("KALE"), P.Fort ? TEXT("Var") : TEXT("Yok")) ]
		+ SVerticalBox::Slot().AutoHeight()
		[
			SNew(SHorizontalBox)
			+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(FMargin(0.f, 1.f, 8.f, 1.f))
			[
				SNew(SBox).WidthOverride(84.f)
				[
					SNew(STextBlock).Text(FText::FromString(TEXT("SİPER"))).Font(Bold(10)).ColorAndOpacity(FSlateColor(InkSoft))
				]
			]
			+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)[ Boxes ]
		];
}

TSharedRef<SWidget> SCepheHUD::BuildArmy(const FArmyRecord& A)
{
	const FProvinceRow* Loc = Map.IsValid() ? Map->FindProvince(A.Province) : nullptr;
	const FLinearColor OrgColor = FMath::Lerp(RedInk, S(60, 120, 50), A.Organization);

	TSharedRef<SVerticalBox> Box = SNew(SVerticalBox);
	Box->AddSlot().AutoHeight().Padding(FMargin(0.f, 0.f, 0.f, 6.f))
	[
		SNew(STextBlock).Text(FText::FromString(A.Name.ToUpper())).Font(Bold(16)).ColorAndOpacity(FSlateColor(Ink))
	];
	Box->AddSlot().AutoHeight()[ Row(TEXT("ÜLKE"), NationName(A.Nation)) ];
	Box->AddSlot().AutoHeight()[ Row(TEXT("KONUM"), Loc ? Loc->Name : FString::Printf(TEXT("#%d"), A.Province)) ];
	Box->AddSlot().AutoHeight()[ Row(TEXT("TÜMEN"), FString::FromInt(A.Divisions)) ];
	Box->AddSlot().AutoHeight().Padding(FMargin(0.f, 1.f))
	[
		SNew(SHorizontalBox)
		+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center).Padding(FMargin(0.f, 0.f, 8.f, 0.f))
		[
			SNew(SBox).WidthOverride(84.f)
			[
				SNew(STextBlock).Text(FText::FromString(TEXT("ORGANİZASYON"))).Font(Bold(8)).ColorAndOpacity(FSlateColor(InkSoft))
			]
		]
		+ SHorizontalBox::Slot().AutoWidth()[ Bar(A.Organization, OrgColor, 150.f) ]
		+ SHorizontalBox::Slot().AutoWidth().Padding(FMargin(6.f, 0.f, 0.f, 0.f))
		[
			SNew(STextBlock).Text(FText::FromString(FString::Printf(TEXT("%%%d"), FMath::RoundToInt(A.Organization * 100.f))))
			.Font(Mono(11)).ColorAndOpacity(FSlateColor(Ink))
		]
	];
	// Tumen basina cubuk (ordu organizasyonu tumenlere ayni uygulanir; tumen verisi henuz yok).
	const int32 Shown = FMath::Min(A.Divisions, 10);
	for (int32 i = 0; i < Shown; ++i)
	{
		Box->AddSlot().AutoHeight().Padding(FMargin(0.f, 1.f))
		[
			SNew(SHorizontalBox)
			+ SHorizontalBox::Slot().AutoWidth().VAlign(VAlign_Center)
			[
				SNew(SBox).WidthOverride(92.f)
				[
					SNew(STextBlock).Text(FText::FromString(FString::Printf(TEXT("%d. Tümen"), i + 1))).Font(Mono(10)).ColorAndOpacity(FSlateColor(Ink))
				]
			]
			+ SHorizontalBox::Slot().AutoWidth()[ Bar(A.Organization, OrgColor, 120.f) ]
		];
	}
	return Box;
}

TSharedRef<SWidget> SCepheHUD::BuildLayers()
{
	TSharedRef<SHorizontalBox> Buttons = SNew(SHorizontalBox);
	for (int32 i = 0; i < 4; ++i)
	{
		TWeakObjectPtr<UProvinceMapSubsystem> M = Map;
		Buttons->AddSlot().AutoWidth().Padding(FMargin(2.f, 0.f))
		[
			MakeButton(FString::Printf(TEXT("%d %s"), i + 1, LayerNames[i]),
				[M, i]() { if (M.IsValid()) M->SetMapMode(static_cast<EMapMode>(i)); },
				[M, i]() { return M.IsValid() && static_cast<int32>(M->GetMapMode()) == i; }, 12)
		];
	}
	return Panel(
		SNew(SVerticalBox)
		+ SVerticalBox::Slot().AutoHeight().Padding(FMargin(0.f, 0.f, 0.f, 4.f))
		[
			SNew(STextBlock).Text(FText::FromString(TEXT("KATMAN"))).Font(Bold(11)).ColorAndOpacity(FSlateColor(RedInk))
		]
		+ SVerticalBox::Slot().AutoHeight()[ Buttons ]
		+ SVerticalBox::Slot().AutoHeight().Padding(FMargin(0.f, 6.f, 0.f, 0.f))
		[
			SNew(STextBlock)
			.Text_Lambda([this]()
			{
				const FProvinceRow* P = Map.IsValid() ? Map->FindProvince(Map->GetHoveredProvince()) : nullptr;
				return FText::FromString(P ? FString::Printf(TEXT("Üstünde: %s"), *P->Name) : FString());
			})
			.Font(Mono(10)).ColorAndOpacity(FSlateColor(InkSoft))
		],
		FMargin(8.f));
}

void SCepheHUD::Construct(const FArguments& InArgs)
{
	Map = InArgs._Map;
	Clock = InArgs._Clock;
	Controller = InArgs._Controller;
	PlayerNation = InArgs._PlayerNation;

	ChildSlot
	[
		SNew(SOverlay)
		.Visibility(EVisibility::SelfHitTestInvisible)
		+ SOverlay::Slot().HAlign(HAlign_Fill).VAlign(VAlign_Top).Padding(FMargin(8.f))
		[
			BuildTopBar()
		]
		+ SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Top).Padding(FMargin(8.f, 84.f, 0.f, 0.f))
		[
			BuildLeftMenu()
		]
		+ SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Top).Padding(FMargin(0.f, 84.f, 8.f, 0.f))
		[
			BuildTelegraph()
		]
		+ SOverlay::Slot().HAlign(HAlign_Left).VAlign(VAlign_Bottom).Padding(FMargin(8.f))
		[
			BuildSelection()
		]
		+ SOverlay::Slot().HAlign(HAlign_Right).VAlign(VAlign_Bottom).Padding(FMargin(8.f))
		[
			BuildLayers()
		]
	];
}

bool SCepheHUD::IsPointerOverUI() const
{
	for (const TSharedPtr<SWidget>& W : HoverPanels)
	{
		if (W.IsValid() && W->IsHovered()) return true;
	}
	return false;
}
