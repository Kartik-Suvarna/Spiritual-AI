from flask import Flask, render_template, request, redirect, flash, url_for
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flashing messages

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'contact.spiritual.ai@gmail.com'  # Sender Email
app.config['MAIL_PASSWORD'] = 'aclh cbbj bbry dbxv'       # Use App Password from Gmail

mail = Mail(app)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        subject = request.form['subject']
        message = request.form['message']

        msg = Message(
            subject=f"New Message: {subject}",
            sender=email,
            recipients=['contact.spiritual.ai@gmail.com']
        )
        msg.body = f"""
        Full Name: {full_name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        Message: {message}
        """
        try:
            mail.send(msg)
            flash("Message sent successfully!", "success")
            return redirect(url_for('contact'))
        except Exception as e:
            flash(f"Failed to send message. Error: {str(e)}", "danger")
            return redirect(url_for('contact'))

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
