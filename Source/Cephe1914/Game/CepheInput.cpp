#include "Game/CepheInput.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "InputCoreTypes.h"

void UCepheInputConfig::Build()
{
	if (bBuilt) return;
	bBuilt = true;

	Context = NewObject<UInputMappingContext>(this, TEXT("IMC_Cephe"));

	auto Make = [this](const TCHAR* Name, EInputActionValueType Type)
	{
		UInputAction* A = NewObject<UInputAction>(this, Name);
		A->ValueType = Type;
		return A;
	};

	Click = Make(TEXT("IA_Click"), EInputActionValueType::Boolean);
	Move = Make(TEXT("IA_Move"), EInputActionValueType::Axis2D);
	Zoom = Make(TEXT("IA_Zoom"), EInputActionValueType::Axis1D);
	Rotate = Make(TEXT("IA_Rotate"), EInputActionValueType::Axis1D);
	Pause = Make(TEXT("IA_Pause"), EInputActionValueType::Boolean);
	SpeedUp = Make(TEXT("IA_SpeedUp"), EInputActionValueType::Boolean);
	SpeedDown = Make(TEXT("IA_SpeedDown"), EInputActionValueType::Boolean);
	Mode1 = Make(TEXT("IA_Mode1"), EInputActionValueType::Boolean);
	Mode2 = Make(TEXT("IA_Mode2"), EInputActionValueType::Boolean);
	Mode3 = Make(TEXT("IA_Mode3"), EInputActionValueType::Boolean);
	Mode4 = Make(TEXT("IA_Mode4"), EInputActionValueType::Boolean);
	Menu1 = Make(TEXT("IA_Menu1"), EInputActionValueType::Boolean);
	Menu2 = Make(TEXT("IA_Menu2"), EInputActionValueType::Boolean);
	Menu3 = Make(TEXT("IA_Menu3"), EInputActionValueType::Boolean);
	Menu4 = Make(TEXT("IA_Menu4"), EInputActionValueType::Boolean);
	Menu5 = Make(TEXT("IA_Menu5"), EInputActionValueType::Boolean);
	Menu6 = Make(TEXT("IA_Menu6"), EInputActionValueType::Boolean);

	Context->MapKey(Click, EKeys::LeftMouseButton);
	Context->MapKey(Pause, EKeys::SpaceBar);
	Context->MapKey(SpeedUp, EKeys::Equals);
	Context->MapKey(SpeedUp, EKeys::Add);
	Context->MapKey(SpeedDown, EKeys::Hyphen);
	Context->MapKey(SpeedDown, EKeys::Subtract);
	Context->MapKey(Mode1, EKeys::One);
	Context->MapKey(Mode2, EKeys::Two);
	Context->MapKey(Mode3, EKeys::Three);
	Context->MapKey(Mode4, EKeys::Four);
	Context->MapKey(Menu1, EKeys::F1);
	Context->MapKey(Menu2, EKeys::F2);
	Context->MapKey(Menu3, EKeys::F3);
	Context->MapKey(Menu4, EKeys::F4);
	Context->MapKey(Menu5, EKeys::F5);
	Context->MapKey(Menu6, EKeys::F6);

	// Hareket: W/S ileri-geri (Y ekseni), A/D sol-sag (X ekseni).
	auto MapMove = [this](const FKey& Key, bool bSwizzleToY, bool bNegate)
	{
		FEnhancedActionKeyMapping& M = Context->MapKey(Move, Key);
		if (bSwizzleToY)
		{
			UInputModifierSwizzleAxis* Sw = NewObject<UInputModifierSwizzleAxis>(Context);
			Sw->Order = EInputAxisSwizzle::YXZ;
			M.Modifiers.Add(Sw);
		}
		if (bNegate)
		{
			M.Modifiers.Add(NewObject<UInputModifierNegate>(Context));
		}
	};
	MapMove(EKeys::W, true, false);
	MapMove(EKeys::Up, true, false);
	MapMove(EKeys::S, true, true);
	MapMove(EKeys::Down, true, true);
	MapMove(EKeys::D, false, false);
	MapMove(EKeys::Right, false, false);
	MapMove(EKeys::A, false, true);
	MapMove(EKeys::Left, false, true);

	Context->MapKey(Zoom, EKeys::MouseWheelAxis);
	Context->MapKey(Rotate, EKeys::E);
	FEnhancedActionKeyMapping& Q = Context->MapKey(Rotate, EKeys::Q);
	Q.Modifiers.Add(NewObject<UInputModifierNegate>(Context));
}
