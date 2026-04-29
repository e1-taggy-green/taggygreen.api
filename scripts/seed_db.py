import sys
import os
import random
from datetime import datetime, timedelta
from faker import Faker

# Garante que a raiz do projeto esteja no PYTHONPATH para importar os serviços
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.esg_engine import ESGEngine
from src.schemas.esg import VehicleEmissionFactors
from src.models import Base, Company, Vehicle, Passage

# ---------------------------------------------------------
# 2. LÓGICA DE INJEÇÃO (SEEDING)
# ---------------------------------------------------------
def run_seeder(total_passages: int = 10000, batch_size: int = 2000):
    print(f"🌱 Iniciando Seeding TaggyGreen: {total_passages} passagens...")
    
    # Conecta no SQLite local documentado no README
    engine = create_engine("sqlite:///taggy_green.db")
    Base.metadata.drop_all(bind=engine)  # Limpa o banco antigo para evitar conflitos de schema
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    faker = Faker('pt_BR')
    esg_engine = ESGEngine()

    try:
        # A. Gerar Empresas (Frotas B2B)
        print("🏢 Gerando 20 Empresas B2B...")
        companies = []
        for _ in range(20):
            comp = Company(cnpj=faker.cnpj(), name=faker.company())
            companies.append(comp)
        db.add_all(companies)
        db.commit()

        # B. Gerar Veículos Realistas (Carros, Motos e Caminhões Pesados)
        print("🚗 Gerando 500 Veículos para as Frotas...")
        vehicles = []
        vehicle_types = [
            {"type": "Carro Leve", "fe": 2.30, "idle": 0.02, "accel": 0.05},
            {"type": "Caminhão Pesado", "fe": 2.68, "idle": 0.06, "accel": 0.15},
            {"type": "Moto", "fe": 2.30, "idle": 0.01, "accel": 0.02}
        ]
        
        for _ in range(500):
            v_type = random.choice(vehicle_types)
            vehicle = Vehicle(
                license_plate=faker.license_plate(),
                vehicle_type=v_type["type"],
                emission_factor_kg_per_l=v_type["fe"],
                idle_fuel_consumption_l_per_min=v_type["idle"],
                accel_brake_extra_fuel_l=v_type["accel"],
                company=random.choice(companies)
            )
            vehicles.append(vehicle)
        db.add_all(vehicles)
        db.commit()

        # C. Gerar Passagens (Bulk Insert / Batches)
        print(f"🛣️ Gerando {total_passages} Passagens no histórico (4 meses)...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120) # 4 Meses atrás

        passages_batch = []
        for i in range(1, total_passages + 1):
            vehicle = random.choice(vehicles)
            # Intercalando uso de Tag (60% usam tag, 40% pararam na guarita)
            has_tag = random.choices([True, False], weights=[0.6, 0.4])[0] 
            
            # Consumo simulado da viagem (orgânico) e tempo perdido na fila
            base_fuel = round(random.uniform(2.0, 50.0), 2)
            idle_time = round(random.uniform(1.0, 5.0), 1) if not has_tag else 0.0
            
            # Puxa os dados para validar na Engine (O Coração Matemático)
            v_factors = VehicleEmissionFactors(
                emission_factor_kg_per_l=vehicle.emission_factor_kg_per_l,
                idle_fuel_consumption_l_per_min=vehicle.idle_fuel_consumption_l_per_min,
                accel_brake_extra_fuel_l=vehicle.accel_brake_extra_fuel_l
            )
            
            # A Mágica! Calcula os dados ESG em tempo real usando a Engine
            resultado = esg_engine.calculate_passagem(
                base_fuel_l=base_fuel, vehicle_factors=v_factors, has_tag=has_tag, idle_time_min=idle_time
            )
            
            passages_batch.append(Passage(
                timestamp=faker.date_time_between(start_date=start_date, end_date=end_date),
                vehicle_id=vehicle.id,
                has_tag=has_tag,
                base_fuel_l=base_fuel,
                idle_time_min=idle_time,
                total_co2_kg=resultado.total_co2_kg,
                total_fuel_l=resultado.total_fuel_l,
                waste_co2_kg=resultado.waste_co2_kg,
                waste_fuel_l=resultado.waste_fuel_l,
                paper_used=resultado.paper_used
            ))

            # Previne estouro de memória inserindo em pacotes de 2000
            if i % batch_size == 0:
                db.bulk_save_objects(passages_batch)
                db.commit()
                print(f"   -> Lote salvo: {i}/{total_passages} passagens...")
                passages_batch.clear() # Limpa a RAM

        print("✅ Seeding finalizado com Sucesso! O Front-end já pode testar o Dashboard!")
    except Exception as e:
        print(f"❌ Erro durante o seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()
