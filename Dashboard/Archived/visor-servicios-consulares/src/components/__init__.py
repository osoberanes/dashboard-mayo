"""
Componentes reutilizables del dashboard
"""

from .kpi_cards import (
    create_kpi_card, create_kpi_row, create_summary_stats_card,
    create_metric_comparison_table, create_loading_spinner,
    create_alert_message, create_info_tooltip, create_progress_bar
)

from .filters import (
    create_date_range_picker, create_service_selector, create_category_selector,
    create_temporal_grouping_selector, create_metric_selector, create_top_n_selector,
    create_filter_panel, create_quick_filters, create_search_filter,
    create_filter_reset_button, create_export_button
)

from .navigation import (
    create_navbar, create_sidebar, create_breadcrumb, create_page_header,
    create_tab_container, create_modal, create_offcanvas_menu,
    create_responsive_layout, create_footer, create_status_indicator
)

__all__ = [
    # KPI Cards
    'create_kpi_card', 'create_kpi_row', 'create_summary_stats_card',
    'create_metric_comparison_table', 'create_loading_spinner',
    'create_alert_message', 'create_info_tooltip', 'create_progress_bar',
    
    # Filters
    'create_date_range_picker', 'create_service_selector', 'create_category_selector',
    'create_temporal_grouping_selector', 'create_metric_selector', 'create_top_n_selector',
    'create_filter_panel', 'create_quick_filters', 'create_search_filter',
    'create_filter_reset_button', 'create_export_button',
    
    # Navigation
    'create_navbar', 'create_sidebar', 'create_breadcrumb', 'create_page_header',
    'create_tab_container', 'create_modal', 'create_offcanvas_menu',
    'create_responsive_layout', 'create_footer', 'create_status_indicator'
]