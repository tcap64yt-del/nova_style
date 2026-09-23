from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.admin_login, name="admin_login"),
    path("logout/", views.admin_logout, name="admin_logout"),
    path("user-management/", views.user_management, name="user_management"),
    path("category-management/", views.category_management, name="category_management"),
    path("category-management/new-category/", views.new_category, name="new_category"),
    path(
        "category-management/edit-category/<int:category_id>",
        views.edit_category,
        name="edit_category",
    ),
    path(
        "category-management/edit-category/status/<int:category_id>",
        views.category_status,
        name="category_status",
    ),
    path("product-management/", views.product_management, name="product_management"),
    path(
        "product-management/activate/<int:product_id>/",
        views.activate_product,
        name="activate_product",
    ),
    path(
        "product-management/deactivate/<int:product_id>/",
        views.deactivate_product,
        name="deactivate_product",
    ),
    path("product-management/add-product/", views.add_product, name="add_product"),
    path(
        "product-management/edit-product/<int:product_id>",
        views.edit_product,
        name="edit_product",
    ),
    path(
        "admin/user-management/block/<int:user_id>/",
        views.block_user,
        name="block_user",
    ),
    path(
        "admin/user-management/unblock/<int:user_id>/",
        views.unblock_user,
        name="unblock_user",
    ),
    path("order-management/", views.order_management, name="order_management"),
    path(
        "admin-order-detail/<int:order_id>/",
        views.admin_order_detail,
        name="admin_order_detail",
    ),
    path(
        "admin-order-detail/<int:order_id>/status",
        views.order_status,
        name="order_status",
    ),
    path("admin-order-returns/", views.admin_order_returns, name="admin_order_returns"),
    path(
        "admin-order-returns/details/<str:return_type>/<int:return_id>/",
        views.return_details,
        name="return_details",
    ),
    path(
        "admin-order-returns/details/<str:return_type>/<int:return_id>/status/",
        views.update_return_status,
        name="update_return_status",
    ),
    path("coupon-management/", views.admin_coupon_management, name="coupon_management"),
    path("coupon-management/add-coupon/", views.add_coupon, name="add_coupon"),
    path(
        "coupon-management/delete/<int:coupon_id>/",
        views.delete_coupon,
        name="delete_coupon",
    ),
    path(
        "coupon-management/edit-coupon/<int:coupon_id>/",
        views.edit_coupon,
        name="edit_coupon",
    ),
    path("sales-report/", views.sales_report, name="sales_report"),
    path("sales-report/pdf/", views.sales_report_pdf, name="sales_report_pdf"),
    path("sales-report/excel/", views.sales_report_excel, name="sales_report_excel"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
