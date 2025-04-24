from itertools import combinations
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from app.models.schemas import Empresa, MatchResult, MatchConfig
from app.models.sector_matrix import SectorMatrixService


class MatchingService:
    @staticmethod
    def calcular_match_mase(
        emp1: Empresa, 
        emp2: Empresa, 
        ecosystem_id: str,
        db: Session,
        config: Optional[MatchConfig] = None
    ) -> MatchResult:
        """
        Calcula el nivel de compatibilidad entre dos empresas.
        
        Args:
            emp1: Primera empresa
            emp2: Segunda empresa
            ecosystem_id: ID del ecosistema
            config: Configuración de pesos para cada factor
            
        Returns:
            Resultado del match con todos los detalles
        """
        if config is None:
            config = MatchConfig()
            
        objetivos = [
            'crear_nuevos_modelos_negocio', 'generar_eficiencias',
            'fidelizar_mercado_actual', 'diversificar_mercado'
        ]
        intereses = [
            'incremento_ventas', 'llegar_nuevos_mercados', 'lanzamiento_nuevos_productos',
            'mejoramiento_productividad', 'incremento_capacidad_productiva',
            'desarrollo_nuevos_canales', 'implementacion_ti',
            'infraestructura_fisica', 'compra_maquinaria_equipos'
        ]
        
        # Convertir Empresa a diccionario para mantener compatibilidad con el código original
        emp1_dict = emp1.dict()
        emp2_dict = emp2.dict()
        
        estrategia_cols = objetivos + intereses
        s1 = [emp1_dict[col] for col in estrategia_cols]
        s2 = [emp2_dict[col] for col in estrategia_cols]
        
        match_afinidad = sum(s1[i] == s2[i] for i in range(len(s1)))
        match_sinergia = sum((s1[i] == 1 and s2[i] == 0) or (s1[i] == 0 and s2[i] == 1) for i in range(len(s1)))
        
        e1 = emp1_dict["num_empleados_directos"] + emp1_dict["num_empleados_indirectos"]
        e2 = emp2_dict["num_empleados_directos"] + emp2_dict["num_empleados_indirectos"]
        diferencia_emp = abs(e1 - e2)
        match_empleados = 1 / (1 + diferencia_emp)
        
        match_ciudad = 1 if emp1_dict["ciudad"] == emp2_dict["ciudad"] else 0
        match_tamaño = 1 if emp1_dict["tamaño"] == emp2_dict["tamaño"] else 0
        
        codigo1 = str(emp1_dict["codigo_ciiu"])
        codigo2 = str(emp2_dict["codigo_ciiu"])
        
        # Usar el servicio de matriz sectorial para obtener la compatibilidad
        match_sector = SectorMatrixService.get_compatibility(codigo1, codigo2, db)
            
        # Aplicar pesos a cada factor
        match_total = (
            match_afinidad * config.peso_afinidad
            + match_sinergia * config.peso_sinergia
            + match_empleados * config.peso_empleados
            + match_ciudad * config.peso_ciudad
            + match_tamaño * config.peso_tamaño
            + match_sector * config.peso_sector
        )
        
        # Generar explicaciones
        if match_afinidad > 0:
            exp_afinidad = f"Coinciden en {match_afinidad} objetivos/intereses."
        else:
            exp_afinidad = "No comparten objetivos/intereses."
            
        if match_sinergia > 0:
            exp_sinergia = f"Tienen sinergia en {match_sinergia} objetivo(s)/interés(es)."
        else:
            exp_sinergia = "No presentan sinergia estratégica."
            
        if diferencia_emp == 0:
            exp_empleados = (
                f"Misma cantidad de empleados ({e1}). "
                f"Contribuye {match_empleados:.2f} al puntaje."
            )
        else:
            if match_empleados > 0.0:
                exp_empleados = (
                    f"Diferencia de empleados: {diferencia_emp}, "
                    f"contribuye {match_empleados:.2f} al puntaje."
                )
            else:
                exp_empleados = (
                    f"Diferencia de empleados muy alta ({diferencia_emp}), "
                    f"no aporta puntaje."
                )
                
        exp_ciudad = (
            "Coinciden en la misma ciudad."
            if match_ciudad == 1 else "No coinciden en la ciudad."
        )
        
        exp_tamaño = (
            "Mismo tamaño empresarial."
            if match_tamaño == 1 else "Diferente tamaño empresarial."
        )
        
        if match_sector > 0:
            exp_sector = f"Compatibilidad sectorial de {match_sector:.2f}."
        else:
            exp_sector = "Sin coincidencia sectorial."
            
        desc_ciiu_1 = emp1_dict.get("descripcion_ciiu", "")
        desc_ciiu_2 = emp2_dict.get("descripcion_ciiu", "")
        
        return MatchResult(
            nit_1=emp1_dict["nit"],
            razon_social_1=emp1_dict["razonsocial"],
            empresa_1=emp1_dict["nombrecomercial"],
            ciiu_1=codigo1,
            descripcion_ciiu_1=desc_ciiu_1,
            nit_2=emp2_dict["nit"],
            razon_social_2=emp2_dict["razonsocial"],
            empresa_2=emp2_dict["nombrecomercial"],
            ciiu_2=codigo2,
            descripcion_ciiu_2=desc_ciiu_2,
            ciudad_1=emp1_dict["ciudad"],
            ciudad_2=emp2_dict["ciudad"],
            tamaño_1=emp1_dict["tamaño"],
            tamaño_2=emp2_dict["tamaño"],
            match_afinidad=match_afinidad,
            match_sinergia=match_sinergia,
            total_empleados_1=e1,
            total_empleados_2=e2,
            diferencia_empleados=diferencia_emp,
            match_ciudad=match_ciudad,
            match_tamaño=match_tamaño,
            match_sector=match_sector,
            puntaje_total=match_total,
            exp_afinidad=exp_afinidad,
            exp_sinergia=exp_sinergia,
            exp_empleados=exp_empleados,
            exp_ciudad=exp_ciudad,
            exp_tamaño=exp_tamaño,
            exp_sector=exp_sector
        )

    @staticmethod
    def generar_matching_mase(
        empresas: List[Empresa], 
        ecosystem_id: str,
        db: Session,
        config: Optional[MatchConfig] = None,
    ) -> List[MatchResult]:
        """
        Genera todos los posibles emparejamientos entre las empresas proporcionadas.
        
        Args:
            empresas: Lista de empresas a emparejar
            ecosystem_id: ID del ecosistema
            config: Configuración de pesos para cada factor
            
        Returns:
            Lista de resultados de match ordenados por puntaje total
        """
        if config is None:
            config = MatchConfig()
            
        matches = []
        for emp1, emp2 in combinations(empresas, 2):
            match_info = MatchingService.calcular_match_mase(
                emp1, emp2, ecosystem_id, db, config
            )
            
            matches.append(match_info)
            
        # Ordenar por puntaje total
        matches.sort(key=lambda x: x.puntaje_total, reverse=True)
        
        return matches
