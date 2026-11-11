import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { clearAuthData, API_BASE_URL, fetchWithTokenRefresh, getAccessToken } from '../utils/auth'

const trackingStatuses = [
  'Pending',
  'Confirmed',
  'Processing',
  'Shipped',
  'Delivered',
]

const trackingLabels = {
  Pending: 'Pending Approval',
  Confirmed: 'Confirmed',
  Processing: 'Processing',
  Shipped: 'Shipped',
  Delivered: 'Delivered',
  Cancelled: 'Cancelled',
}

function OrderTracking({ status }) {
  const isCancelled = status === 'Cancelled'
  const statuses = isCancelled
    ? ['Pending', 'Cancelled']
    : trackingStatuses
  const currentIndex = trackingStatuses.indexOf(status)

  return (
    <section className="order-tracking">
      <h3>Order Tracking</h3>

      <div className="tracking-timeline">
        {statuses.map((trackingStatus, index) => {
          const isCurrent = isCancelled
            ? trackingStatus === 'Cancelled'
            : index === currentIndex
          const isCompleted = isCancelled
            ? trackingStatus === 'Pending'
            : index < currentIndex
          const state = isCurrent
            ? 'current'
            : isCompleted
              ? 'completed'
              : 'upcoming'

          return (
            <div
              className={`tracking-step ${state} ${isCancelled ? 'cancelled-flow' : ''}`}
              key={trackingStatus}
            >
              <div className="tracking-step-content">
                <span className="tracking-icon" aria-hidden="true">
                  {isCancelled && trackingStatus === 'Cancelled'
                    ? '✕'
                    : isCompleted
                      ? '✓'
                      : isCurrent
                        ? '●'
                        : '○'}
                </span>
                <span className="tracking-label">
                  {trackingLabels[trackingStatus]}
                </span>
              </div>

              {index < statuses.length - 1 && (
                <span
                  className={`tracking-line ${isCompleted ? 'completed' : ''}`}
                  aria-hidden="true"
                />
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}

function MyOrders() {
  const navigate = useNavigate()

  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  useEffect(() => {
    const loadOrders = async () => {
      if (!getAccessToken()) {
        navigate('/login')
        return
      }

      try {
        const response = await fetchWithTokenRefresh(
          `${API_BASE_URL}/api/orders/my-orders/`,
          {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
          },
        )

        if (response.status === 401) {
          clearAuthData()
          navigate('/login')
          return
        }

        const data = await response.json()

        console.log(
          'MY ORDERS STATUS:',
          response.status
        )

        console.log(
          'MY ORDERS RESPONSE:',
          data
        )

        if (!response.ok) {
          throw new Error(
            data.error ||
            data.detail ||
            'Failed to load orders.'
          )
        }

        setOrders(data)
        setLoading(false)

      } catch (error) {
        console.error(
          'MY ORDERS ERROR:',
          error
        )

        setError(error.message)
        setLoading(false)
      }
    }

    loadOrders()

  }, [navigate])

  const handleCancelOrder = async (orderId) => {
    const confirmed = window.confirm(
      'Are you sure you want to cancel this order?'
    )

    if (!confirmed) {
      return
    }

    try {
      const response = await fetchWithTokenRefresh(
        `${API_BASE_URL}/api/orders/${orderId}/cancel/`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
        },
      )

      if (response.status === 401) {
        clearAuthData()
        navigate('/login')
        return
      }

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.error || data.detail || 'Failed to cancel order.'
        )
      }

      setError('')
      setSuccessMessage('Order cancelled successfully.')

      setOrders((currentOrders) =>
        currentOrders.map((order) =>
          order.id === orderId
            ? { ...order, status: data.status }
            : order
        )
      )
    } catch (error) {
      setSuccessMessage('')
      alert(error.message)
    }
  }

  if (loading) {
    return (
      <main className="my-orders-page">
        <h1>My Orders</h1>
        <p>Loading orders...</p>
      </main>
    )
  }


  if (error) {
    return (
      <main className="my-orders-page">
        <h1>My Orders</h1>

        <div className="orders-error">
          {error}
        </div>
      </main>
    )
  }


  return (
    <main className="my-orders-page">

      <div className="my-orders-header">

        <div>
          <h1>My Orders</h1>

          <p>
            View your previous orders and order details.
          </p>
        </div>

        <Link
          to="/"
          className="orders-shopping-button"
        >
          Continue Shopping
        </Link>

      </div>

      {successMessage && (
        <div className="orders-success-message">
          {successMessage}
        </div>
      )}

      {orders.length === 0 ? (

        <div className="no-orders">

          <h2>No Orders Yet</h2>

          <p>
            You have not placed any orders yet.
          </p>

          <Link
            to="/"
            className="orders-shopping-button"
          >
            Start Shopping
          </Link>

        </div>

      ) : (

        <div className="orders-list">

          {orders.map((order) => (

            <div
              className="order-card"
              key={order.id}
            >

              <div className="order-card-header">

                <div>

                  <span className="order-label">
                    Order Number
                  </span>

                  <strong>
                    {order.order_number}
                  </strong>

                </div>

                <div className="order-header-actions">
                  <div
                    className={`order-status status-${order.status.toLowerCase()}`}
                  >
                    {order.status}
                  </div>

                  <a
                    className="cancel-order-button"
                    href={`${API_BASE_URL}/api/orders/${order.id}/invoice/`}
                    onClick={(event) => {
                      event.preventDefault()
                      fetchWithTokenRefresh(`${API_BASE_URL}/api/orders/${order.id}/invoice/`)
                        .then((res) => res.blob())
                        .then((blob) => {
                          const url = URL.createObjectURL(blob)
                          const anchor = document.createElement('a')
                          anchor.href = url
                          anchor.download = `invoice-${order.order_number}.pdf`
                          anchor.click()
                          URL.revokeObjectURL(url)
                        })
                        .catch(() => alert('Could not download invoice.'))
                    }}
                  >
                    Invoice PDF
                  </a>

                  {order.status !== 'Cancelled' &&
                    order.status !== 'Delivered' &&
                    order.status !== 'Shipped' && (
                      <button
                        type="button"
                        className="cancel-order-button"
                        onClick={() => handleCancelOrder(order.id)}
                      >
                        Cancel Order
                      </button>
                    )}
                </div>

              </div>

              <OrderTracking status={order.status} />


              <div className="order-card-info">

                <div>
                  <span>Date</span>

                  <strong>
                    {new Date(
                      order.created_at
                    ).toLocaleDateString()}
                  </strong>
                </div>


                <div>
                  <span>Payment</span>

                  <strong>
                    {order.payment_method}
                  </strong>
                </div>


                <div>
                  <span>Delivery</span>

                  <strong>
                    {order.delivery_method}
                  </strong>
                </div>


                <div>
                  <span>Total</span>

                  <strong>
                    ৳
                    {Number(
                      order.total
                    ).toFixed(2)}
                  </strong>
                </div>

              </div>


              <div className="order-products">

                <h3>Products</h3>

                {order.items.map((item) => (

                  <div
                    className="order-product"
                    key={item.id}
                  >

                    <div>

                      <strong>
                        {item.product_name}
                      </strong>

                      <span>
                        Quantity: {item.quantity}
                      </span>

                    </div>

                    <strong>
                      ৳
                      {Number(
                        item.subtotal
                      ).toFixed(2)}
                    </strong>

                  </div>

                ))}

              </div>


              <div className="order-card-footer">

                <span>
                  Delivery: ৳
                  {Number(
                    order.delivery_fee
                  ).toFixed(2)}
                </span>


                {Number(order.discount) > 0 && (

                  <span>
                    Discount: -৳
                    {Number(
                      order.discount
                    ).toFixed(2)}
                  </span>

                )}


                <strong>
                  Total: ৳
                  {Number(
                    order.total
                  ).toFixed(2)}
                </strong>

              </div>

            </div>

          ))}

        </div>

      )}

    </main>
  )
}

export default MyOrders