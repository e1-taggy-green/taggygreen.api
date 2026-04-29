from src.schemas.esg import VehicleEmissionFactors, EnvironmentFactors, PassagemResult, ESGSavingResult


class ESGEngine:
    """
    O Coração Matemático ESG do TaggyGreen.
    Responsável por calcular e evidenciar o desperdício ambiental de pedágios manuais
    contra o fluxo contínuo proporcionado pela Tag.
    """
    def __init__(self, env_factors: EnvironmentFactors = EnvironmentFactors()):
        self.env_factors = env_factors

    def calculate_passagem(
        self,
        base_fuel_l: float,
        vehicle_factors: VehicleEmissionFactors,
        has_tag: bool,
        idle_time_min: float = 2.0
    ) -> PassagemResult:
        # 1. E_CT (Cenário Com Tag)
        # Fórmula PDF: E_CT = D_plaza * C_cruise * FE_f (onde base_fuel_l representa D_plaza * C_cruise)
        E_CT_fuel_l = base_fuel_l
        E_CT_co2_kg = E_CT_fuel_l * vehicle_factors.emission_factor_kg_per_l

        if has_tag:
            # Com Tag: Veículo mantém velocidade constante. Retorna apenas E_CT.
            return PassagemResult(
                has_tag=True,
                total_co2_kg=round(E_CT_co2_kg, 4),
                total_fuel_l=round(E_CT_fuel_l, 4),
                waste_co2_kg=0.0,
                waste_fuel_l=0.0,
                paper_used=0
            )
        
        # 2. Detalhamento dos Componentes do Cenário Sem Tag (E_ST)
        
        # E_idle: Emissões de Marcha Lenta (E_idle = T_idle * C_v * FE_f)
        E_idle_fuel_l = idle_time_min * vehicle_factors.idle_fuel_consumption_l_per_min
        E_idle_co2_kg = E_idle_fuel_l * vehicle_factors.emission_factor_kg_per_l
        
        # E_accel: Emissões de Aceleração Extra (E_accel = DeltaFuel * FE_f)
        E_accel_fuel_l = vehicle_factors.accel_brake_extra_fuel_l
        E_accel_co2_kg = E_accel_fuel_l * vehicle_factors.emission_factor_kg_per_l
        
        # E_paper: Emissões do Ciclo do Papel (E_paper = M_ticket * FE_paper)
        E_paper_co2_kg = self.env_factors.paper_ticket_co2_kg

        # Agrupamento dos Desperdícios e Soma Total (E_ST = E_CT + E_idle + E_accel + E_paper)
        waste_fuel_l = E_idle_fuel_l + E_accel_fuel_l
        waste_co2_total = E_idle_co2_kg + E_accel_co2_kg + E_paper_co2_kg

        return PassagemResult(
            has_tag=False,
            total_co2_kg=round(E_CT_co2_kg + waste_co2_total, 4),
            total_fuel_l=round(E_CT_fuel_l + waste_fuel_l, 4),
            waste_co2_kg=round(waste_co2_total, 4),
            waste_fuel_l=round(waste_fuel_l, 4),
            paper_used=1
        )

    def calculate_savings(
        self, base_fuel_l: float, vehicle_factors: VehicleEmissionFactors, idle_time_min: float = 2.0
    ) -> ESGSavingResult:
        result_com_tag = self.calculate_passagem(base_fuel_l, vehicle_factors, has_tag=True, idle_time_min=idle_time_min)
        result_sem_tag = self.calculate_passagem(base_fuel_l, vehicle_factors, has_tag=False, idle_time_min=idle_time_min)

        # A Fórmula Fundamental (PDF): E_saved = E_ST - E_CT
        E_saved_co2 = result_sem_tag.total_co2_kg - result_com_tag.total_co2_kg
        E_saved_fuel = result_sem_tag.total_fuel_l - result_com_tag.total_fuel_l

        return ESGSavingResult(
            co2_saved_kg=round(E_saved_co2, 4),
            fuel_saved_l=round(E_saved_fuel, 4),
            time_saved_min=idle_time_min,
            paper_saved=result_sem_tag.paper_used - result_com_tag.paper_used
        )
