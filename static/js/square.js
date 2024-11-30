// --- Square決済JavaScript --- //
const applicationId = "{{ square_application_id }}";
const locationId = "{{ square_location_id }}";

async function initializeCard() {
  const payments = Square.payments(applicationId, locationId);
  const card = await payments.card();
  await card.attach('#card-container');
  return card;
}

async function handlePaymentMethodSubmission(event, card) {
  event.preventDefault();
  const tokenResult = await card.tokenize();
  if (tokenResult.status !== "OK") {
    console.error(tokenResult.errors);
    return;
  }

  const response = await fetch("{% url 'process_payment' %}", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": "{{ csrf_token }}",
    },
    body: JSON.stringify({
      nonce: tokenResult.token,
      idempotency_key: String(Date.now())
    }),
  });

  if (response.ok) {
    alert("Payment successful!");
  } else {
    console.error("Payment failed!");
  }
}

const card = await initializeCard();
const cardButton = document.getElementById("card-button");
cardButton.addEventListener("click", (event) => handlePaymentMethodSubmission(event, card));