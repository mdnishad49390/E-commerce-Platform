from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def build_order_invoice_pdf(order) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(25 * mm, y, 'TechMart — Tax Invoice')
    y -= 10 * mm

    pdf.setFont('Helvetica', 10)
    pdf.drawString(25 * mm, y, f'Order: {order.order_number}')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Date: {order.created_at.strftime("%Y-%m-%d %H:%M")}')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Customer: {order.first_name} {order.last_name}')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Email: {order.email} | Mobile: {order.mobile}')
    y -= 10 * mm

    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(25 * mm, y, 'Items')
    y -= 7 * mm
    pdf.setFont('Helvetica', 10)

    for item in order.items.select_related('product'):
        line = f'{item.product_name} x{item.quantity} @ ৳{item.price} = ৳{item.subtotal}'
        pdf.drawString(25 * mm, y, line[:95])
        y -= 6 * mm
        if y < 40 * mm:
            pdf.showPage()
            y = height - 25 * mm

    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Subtotal: ৳{order.subtotal}')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Discount: ৳{order.discount}')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Delivery: ৳{order.delivery_fee}')
    y -= 6 * mm
    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(25 * mm, y, f'Total: ৳{order.total}')
    y -= 8 * mm
    pdf.setFont('Helvetica', 10)
    pdf.drawString(25 * mm, y, f'Payment: {order.payment_method} ({order.payment_status})')
    y -= 6 * mm
    pdf.drawString(25 * mm, y, f'Status: {order.status}')

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
