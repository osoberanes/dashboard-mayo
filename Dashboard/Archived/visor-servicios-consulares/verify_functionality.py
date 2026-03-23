"""
Script de verificación funcional del Visor de Servicios Consulares
Usa datos reales del proyecto original para testing
"""
import sys
import os
import pandas as pd
from pathlib import Path
import logging

# Configurar path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core import DatabaseManager, AnalyticsEngine, ChartFactory
from src.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FunctionalityVerifier:
    """Verificador de funcionalidades del sistema"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.analytics = AnalyticsEngine(self.db)
        self.charts = ChartFactory()
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Registra resultado de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        logger.info(f"{status}: {test_name} - {message}")
    
    def test_database_functionality(self):
        """Test funcionalidad de base de datos"""
        logger.info("🗄️ Testing Database Functionality...")
        
        try:
            # Test 1: Creación de base de datos
            stats = self.db.get_summary_stats()
            self.log_test_result(
                "Database Creation", 
                True, 
                f"Database initialized with {stats.get('total_registros', 0)} records"
            )
        except Exception as e:
            self.log_test_result("Database Creation", False, str(e))
        
        try:
            # Test 2: Obtener listas
            services = self.db.get_services_list()
            categories = self.db.get_categories_list()
            self.log_test_result(
                "Database Lists", 
                len(services) > 0 and len(categories) > 0,
                f"Found {len(services)} services, {len(categories)} categories"
            )
        except Exception as e:
            self.log_test_result("Database Lists", False, str(e))
        
        try:
            # Test 3: Rango de fechas
            date_range = self.db.get_date_range()
            self.log_test_result(
                "Date Range",
                date_range.get('total_registros', 0) > 0,
                f"Date range: {date_range.get('fecha_min')} to {date_range.get('fecha_max')}"
            )
        except Exception as e:
            self.log_test_result("Date Range", False, str(e))
    
    def test_analytics_functionality(self):
        """Test funcionalidad de analytics"""
        logger.info("📊 Testing Analytics Functionality...")
        
        try:
            # Test 1: KPIs básicos
            kpis = self.analytics.get_kpis()
            self.log_test_result(
                "Basic KPIs",
                kpis['total_ingresos'] > 0 and kpis['total_tramites'] > 0,
                f"Total: ${kpis['total_ingresos']:,.2f}, {kpis['total_tramites']:,} trámites"
            )
        except Exception as e:
            self.log_test_result("Basic KPIs", False, str(e))
        
        try:
            # Test 2: Análisis temporal
            temporal_data = self.analytics.get_temporal_analysis('mensual')
            self.log_test_result(
                "Temporal Analysis",
                not temporal_data.empty,
                f"Generated {len(temporal_data)} monthly data points"
            )
        except Exception as e:
            self.log_test_result("Temporal Analysis", False, str(e))
        
        try:
            # Test 3: Top servicios
            top_services = self.analytics.get_top_services(by='ingresos', top_n=5)
            self.log_test_result(
                "Top Services",
                not top_services.empty,
                f"Found {len(top_services)} top services"
            )
        except Exception as e:
            self.log_test_result("Top Services", False, str(e))
        
        try:
            # Test 4: Análisis semanal
            weekly_analysis = self.analytics.get_weekly_analysis()
            self.log_test_result(
                "Weekly Analysis",
                'weekly_data' in weekly_analysis,
                f"Max activity: {weekly_analysis.get('max_ingresos_dia', 'N/A')}"
            )
        except Exception as e:
            self.log_test_result("Weekly Analysis", False, str(e))
        
        try:
            # Test 5: Predicción
            prediction = self.analytics.predict_next_period(periods=3)
            self.log_test_result(
                "Prediction Engine",
                'predictions' in prediction,
                f"Generated {len(prediction.get('predictions', {}).get('ingresos', []))} predictions"
            )
        except Exception as e:
            self.log_test_result("Prediction Engine", False, str(e))
    
    def test_charts_functionality(self):
        """Test funcionalidad de gráficas"""
        logger.info("📈 Testing Charts Functionality...")
        
        try:
            # Obtener datos para gráficas
            temporal_data = self.analytics.get_temporal_analysis('mensual')
            
            if not temporal_data.empty:
                # Test 1: Gráfica de líneas
                line_chart = self.charts.create_line_chart(
                    data=temporal_data,
                    x_col='periodo_str',
                    y_col='ingresos_totales',
                    title='Test Line Chart'
                )
                self.log_test_result(
                    "Line Chart Creation",
                    len(line_chart.data) > 0,
                    f"Created line chart with {len(line_chart.data)} traces"
                )
                
                # Test 2: Gráfica de barras
                top_services = self.analytics.get_top_services(by='ingresos', top_n=5)
                if not top_services.empty:
                    bar_chart = self.charts.create_bar_chart(
                        data=top_services,
                        x_col='servicio',
                        y_col='ingresos_totales',
                        title='Test Bar Chart'
                    )
                    self.log_test_result(
                        "Bar Chart Creation",
                        len(bar_chart.data) > 0,
                        f"Created bar chart with {len(top_services)} services"
                    )
                
                # Test 3: KPI Chart
                kpis = self.analytics.get_kpis()
                kpi_chart = self.charts.create_kpi_chart(kpis)
                self.log_test_result(
                    "KPI Chart Creation",
                    len(kpi_chart.data) > 0,
                    f"Created KPI chart with {len(kpi_chart.data)} indicators"
                )
            else:
                self.log_test_result("Charts with Data", False, "No temporal data available")
                
        except Exception as e:
            self.log_test_result("Charts Functionality", False, str(e))
    
    def test_file_loading(self):
        """Test carga de archivo original"""
        logger.info("📁 Testing File Loading...")
        
        original_file_path = Path("../Inicio/mayo.xls")
        
        if original_file_path.exists():
            try:
                # Intentar cargar archivo original como HTML
                df = pd.read_html(str(original_file_path))[0]
                
                # Mapear columnas
                column_mapping = {
                    'Servicio': 'servicio',
                    'Articulo': 'categoria',
                    'Derechos': 'costo_unitario',
                    'No. de trámites': 'num_tramites',
                    'Importe USD': 'ingresos_totales',
                    'Fecha recaudación': 'fecha_emision',
                    'No. cancelados': 'formas_canceladas'
                }
                
                df = df.rename(columns=column_mapping)
                df = df.fillna(0)
                
                self.log_test_result(
                    "Original File Loading",
                    len(df) > 0,
                    f"Loaded {len(df)} records from original file"
                )
                
                # Test inserción en BD
                result = self.db.insert_data(df, 'verification_test.xls')
                self.log_test_result(
                    "File Data Insertion",
                    result['insertados'] > 0,
                    f"Inserted {result['insertados']} records, {result['duplicados']} duplicates"
                )
                
            except Exception as e:
                self.log_test_result("Original File Loading", False, str(e))
        else:
            self.log_test_result(
                "Original File Loading", 
                False, 
                f"Original file not found at {original_file_path}"
            )
    
    def test_configuration(self):
        """Test configuración del sistema"""
        logger.info("⚙️ Testing System Configuration...")
        
        try:
            # Test configuraciones básicas
            self.log_test_result(
                "Settings Loading",
                settings.app.title is not None,
                f"App title: {settings.app.title}"
            )
            
            self.log_test_result(
                "Database Config",
                Path(settings.database.path).parent.exists(),
                f"DB path: {settings.database.path}"
            )
            
            self.log_test_result(
                "Charts Config",
                len(settings.charts.default_colors) > 0,
                f"Loaded {len(settings.charts.default_colors)} color schemes"
            )
            
        except Exception as e:
            self.log_test_result("Configuration", False, str(e))
    
    def test_edge_cases(self):
        """Test casos extremos"""
        logger.info("🧪 Testing Edge Cases...")
        
        try:
            # Test 1: KPIs con fechas vacías
            empty_kpis = self.analytics.get_kpis('2030-01-01', '2030-01-02')
            self.log_test_result(
                "Empty Date Range KPIs",
                empty_kpis['total_ingresos'] == 0,
                "Empty date range handled correctly"
            )
            
            # Test 2: Servicio inexistente
            nonexistent_service = self.analytics.get_service_analysis('Servicio Inexistente')
            self.log_test_result(
                "Nonexistent Service",
                'error' in nonexistent_service,
                "Nonexistent service handled correctly"
            )
            
            # Test 3: Gráfica con datos vacíos
            empty_df = pd.DataFrame()
            empty_chart = self.charts.create_line_chart(
                data=empty_df,
                x_col='x',
                y_col='y',
                title='Empty Chart'
            )
            self.log_test_result(
                "Empty Data Chart",
                len(empty_chart.layout.annotations) > 0,
                "Empty data chart handled correctly"
            )
            
        except Exception as e:
            self.log_test_result("Edge Cases", False, str(e))
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        logger.info("🚀 Starting Functionality Verification...")
        logger.info("=" * 60)
        
        # Ejecutar todos los tests
        self.test_configuration()
        self.test_database_functionality()
        self.test_file_loading()
        self.test_analytics_functionality()
        self.test_charts_functionality()
        self.test_edge_cases()
        
        # Resumen de resultados
        logger.info("=" * 60)
        logger.info("📋 VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"Success Rate: {(passed/len(self.test_results)*100):.1f}%")
        
        if failed > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    logger.info(f"  - {result['test']}: {result['message']}")
        
        logger.info("\n" + "=" * 60)
        
        if failed == 0:
            logger.info("🎉 ALL TESTS PASSED! System is ready for deployment.")
        else:
            logger.info(f"⚠️  {failed} tests failed. Please review and fix issues.")
        
        return failed == 0


def main():
    """Función principal"""
    print("🔍 Visor de Servicios Consulares - Functionality Verification")
    print("=" * 60)
    
    verifier = FunctionalityVerifier()
    success = verifier.run_all_tests()
    
    if success:
        print("\n✅ Verification completed successfully!")
        print("🚀 You can now run the application with: python src/app.py")
    else:
        print("\n❌ Verification found issues that need to be addressed.")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())