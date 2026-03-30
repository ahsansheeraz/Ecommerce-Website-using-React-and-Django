import api from './api';

export const checkoutService = {
  // Create order
  async createOrder(orderData) {
    try {
      const response = await api.post('/orders/checkout/', orderData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get shipping methods
  async getShippingMethods() {
    try {
      const response = await api.get('/shipping/methods/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get payment methods
  async getPaymentMethods() {
    try {
      const response = await api.get('/payments/methods/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Validate coupon
  async validateCoupon(code) {
    try {
      const response = await api.post('/cart/coupons/validate/', { code });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Create payment intent
  async createPaymentIntent(orderId, amount) {
    try {
      const response = await api.post('/payments/create-payment-intent/', {
        order_id: orderId,
        amount
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Confirm payment
  async confirmPayment(transactionId, paymentIntentId) {
    try {
      const response = await api.post('/payments/confirm-payment/', {
        transaction_id: transactionId,
        payment_intent_id: paymentIntentId
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default checkoutService;