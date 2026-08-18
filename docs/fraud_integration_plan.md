# Fraud Check Integration Plan

## Objective

The order-service should call the AI service fraud-check endpoint before processing an order.

## Request Flow

1. User submits an order.
2. Order-service validates the basic order request.
3. Order-service prepares the fraud-check feature payload.
4. Order-service calls:

   POST /ai/fraud-check

5. AI service validates the fraud feature schema.
6. AI service calculates/evaluates the fraud features.
7. AI service returns a fraud-check result.
8. Order-service uses the result to decide whether to:
   - continue processing the order
   - reject the order
   - send the order for additional review

## Fraud Features

The fraud-check request can contain:

- orderId
- userId
- amount
- symbol
- exchange
- side
- orderType
- product
- quantity
- price
- isPaper
- placedAt
- new_device
- location_changed

## Endpoint

POST /ai/fraud-check

### Example request

{
  "orderId": "11111111-1111-1111-1111-111111111111",
  "userId": "22222222-2222-2222-2222-222222222222",
  "amount": 25000,
  "symbol": "RELIANCE",
  "exchange": "NSE",
  "side": "BUY",
  "orderType": "MARKET",
  "product": "CNC",
  "quantity": 10,
  "price": 2500,
  "isPaper": false,
  "placedAt": "2026-08-17T12:00:00Z",
  "new_device": true,
  "location_changed": false
}

## Authentication

Order-service will authenticate requests to the AI service using the shared secret configured between the services.

The shared secret should be sent using the agreed authentication header.

The secret must not be hard-coded.

## Timeout

The order-service should use a short timeout when calling the fraud-check endpoint because fraud checking is part of the order-processing path.

The target for real-time fraud feature calculation is less than 100 ms.

## Failure Handling

If the AI service is unavailable, the order-service should follow the agreed fail-open/fail-closed policy.

This policy must be decided with the backend/security team before production deployment.

## Future Fraud Decision

The current endpoint is only a skeleton.

Future implementation will return a structured fraud decision such as:

{
  "decision": "ALLOW",
  "risk_score": 0.12,
  "reasons": []
}

The exact decision logic and thresholds will be implemented separately.

## Responsibility

### Order-service

- Receive the user's order.
- Validate the order.
- Prepare fraud-check input.
- Call the AI service.
- Apply the fraud decision before processing the order.

### AI-service

- Validate fraud-check input.
- Calculate fraud features.
- Run fraud detection logic/model.
- Return the fraud decision and relevant risk information.

### Kafka

The existing `orders.created` Kafka flow remains useful for asynchronous fraud-event processing and feature/history tracking.

The synchronous fraud-check endpoint is used before the order is processed.