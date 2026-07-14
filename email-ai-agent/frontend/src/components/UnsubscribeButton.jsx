export default function UnsubscribeButton({ email, onUnsubscribe }) {
  const hasMethod = email.unsubscribe_url || email.unsubscribe_mailto;
  if (!hasMethod) return null;

  if (email.unsubscribe_status === "sent") {
    return <span className="unsubscribe-label">Unsubscribed</span>;
  }
  if (email.unsubscribe_status === "opened") {
    return <span className="unsubscribe-label">Unsubscribe link opened</span>;
  }

  return (
    <button className="unsubscribe-button" onClick={() => onUnsubscribe(email)}>
      {email.unsubscribe_status === "failed" ? "Retry unsubscribe" : "Unsubscribe"}
    </button>
  );
}
