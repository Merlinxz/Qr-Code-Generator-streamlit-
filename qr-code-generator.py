import streamlit as st
import qrcode
from PIL import Image, ImageEnhance
from io import BytesIO
import json

# Function to generate the QR code with optional logo
def generate_qr_code(qr_type, data, color, bg_color, box_size, border, version, error_correction, include_logo, logo_file, logo_size_percentage, logo_transparency):
    # Create a QR code object with user-specified settings
    qr = qrcode.QRCode(
        version=version,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )

    # Generate QR code data based on the selected type
    if qr_type == "Text/URL":
        qr.add_data(data)  # Whether it's plain text or a URL, handle it the same way
    elif qr_type == "WiFi":
        ssid = data.get("ssid")
        password = data.get("password")
        wifi_type = data.get("wifi_type", "None")  # Default to "None"
        hidden_network = data.get("hidden_network", False)
        
        if wifi_type == "None":
            st.warning("WiFi type is set to 'None'.")
            # Omitting the WiFi prefix or making it clear that no type is set
            wifi_data = f"WIFI:S:{ssid};P:{password};H:{str(hidden_network).upper()};;"
        else:
            wifi_data = f"WIFI:T:{wifi_type};S:{ssid};P:{password};H:{str(hidden_network).upper()};;"
        qr.add_data(wifi_data)
    elif qr_type == "Email":
        subject = data.get("subject", "")
        body = data.get("body", "")
        email_data = f"mailto:{data['email']}?subject={subject}&body={body}"
        qr.add_data(email_data)
    elif qr_type == "Phone Number/SMS":
        phone_number = data.get("phone_number", "")
        sms_body = data.get("sms_body", "")
        sms_data = f"smsto:{phone_number}?body={sms_body}"
        qr.add_data(sms_data)
    else:
        st.error("Unsupported QR code type.")
        return None

    qr.make(fit=True)

    # Generate QR code image with specified colors
    img = qr.make_image(fill_color=color, back_color=bg_color).convert('RGB')

    # Add a logo to the QR code if enabled
    if include_logo and logo_file:
        try:
            logo = Image.open(logo_file)
            logo_size = int(min(img.size) * (logo_size_percentage / 100))
            logo = logo.resize((logo_size, logo_size))

            # Apply transparency to the logo
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')

            alpha = logo.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(logo_transparency / 100)
            logo.putalpha(alpha)

            # Calculate the position for the logo and paste it onto the QR code
            logo_position = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
            img.paste(logo, logo_position, logo)
        except Exception as e:
            st.error(f"Error adding logo: {e}")

    return img

# Function to load default values from a JSON file
def load_default_values():
    with open('default_values.json', 'r') as file:
        return json.load(file)

def main():
    st.set_page_config(page_title="🌀 QR Code Generator")

    # Load default values
    default_values = load_default_values()

    # QR code type selection
    qr_type = st.selectbox(
        "🔗 Select QR Code Type", 
        ["Text/URL", "WiFi", "Email", "Phone Number/SMS"],
        index=["Text/URL", "WiFi", "Email", "Phone Number/SMS"].index(default_values["qr_type"])
    )

    # Data input fields based on QR type
    data = {}
    if qr_type == "Text/URL":
        data = st.text_input("✏️ Enter Text or URL:", value=default_values["text_url"], placeholder=default_values["text_url_placeholder"])
    elif qr_type == "WiFi":
        ssid = st.text_input("📶 Enter SSID:", value=default_values["ssid"], placeholder=default_values["ssid_placeholder"])
        password = st.text_input("🔑 Enter Password:", value=default_values["password"], placeholder=default_values["password_placeholder"])
        wifi_type = st.selectbox(
            "📡 Select WiFi Type", 
            ["None", "WEP", "WPA", "WPA2"],
            index=["None", "WEP", "WPA", "WPA2"].index(default_values["wifi_type"])
        )
        hidden_network = st.checkbox("🔒 Hidden Network", value=default_values["hidden_network"])
        data = {"ssid": ssid, "password": password, "wifi_type": wifi_type, "hidden_network": hidden_network}
    elif qr_type == "Email":
        email = st.text_input("📧 Enter Email Address:", value=default_values["email"], placeholder=default_values["email_placeholder"])
        subject = st.text_input("📝 Subject (optional):", value=default_values["subject"], placeholder=default_values["subject_placeholder"])
        body = st.text_area("💬 Body (optional):", value=default_values["body"], placeholder=default_values["body_placeholder"])
        data = {"email": email, "subject": subject, "body": body}
    elif qr_type == "Phone Number/SMS":
        phone_number = st.text_input("📱 Enter Phone Number:", value=default_values["phone_number"], placeholder=default_values["phone_number_placeholder"])
        sms_body = st.text_area("✉️ SMS Body (optional):", value=default_values["sms_body"], placeholder=default_values["sms_body_placeholder"])
        data = {"phone_number": phone_number, "sms_body": sms_body}

    if not data:
        st.warning("⚠️ Please enter data for the QR code.")
        return

    # QR code customization options
    col1, col2 = st.columns(2)
    with col1:
        color = st.color_picker("🎨 QR code color", default_values["color"])
    with col2:
        bg_color = st.color_picker("🖼️ Background color", default_values["bg_color"])

    # Box size, border, and version input fields
    col3, col4, col5 = st.columns(3)
    with col3:
        box_size = st.number_input("📦 Box size (1-100)", min_value=1, max_value=100, value=default_values["box_size"])
    with col4:
        border = st.number_input("🧱 Border size (0-10)", min_value=0, max_value=10, value=default_values["border"])
    with col5:
        version = st.number_input("📏 QR Code Version (1-40)", min_value=1, max_value=40, value=default_values["version"])

    # Error correction level, file name, and file type input fields in one row
    col6, col7, col8 = st.columns(3)
    with col6:
        error_correction_levels = [
            qrcode.constants.ERROR_CORRECT_L,
            qrcode.constants.ERROR_CORRECT_M,
            qrcode.constants.ERROR_CORRECT_Q,
            qrcode.constants.ERROR_CORRECT_H
        ]
        error_correction = st.selectbox(
            "🛠️ Error Correction Level",
            options=error_correction_levels,
            format_func=lambda x: ["L (Low)", "M (Medium)", "Q (Quartile)", "H (High)"][error_correction_levels.index(x)],
            index=error_correction_levels.index(qrcode.constants.ERROR_CORRECT_H)
        )
    with col7:
        file_name = st.text_input("💾 Enter file name:", value=default_values["file_name"], placeholder=default_values["file_name_placeholder"]).strip()
    with col8:
        file_type = st.selectbox(
            "📁 Select file type", 
            options=['PNG', 'JPEG', 'JPG', 'WEBP', 'GIF'], 
            index=['PNG', 'JPEG', 'JPG', 'WEBP', 'GIF'].index(default_values["file_type"])
        )

    # Logo options
    include_logo = st.checkbox("🖼️ Include logo", value=default_values["include_logo"])
    if include_logo:
        logo_file = st.file_uploader("Upload logo (PNG, JPEG, JPG, GIF, WEBP)", type=['png', 'jpg', 'jpeg', 'gif', 'webp'])
        
        # Display logo size and transparency sliders in one row
        col9, col10 = st.columns(2)
        with col9:
            logo_size_percentage = st.number_input("🔳 Logo size (%)", min_value=1, max_value=100, value=default_values["logo_size_percentage"])
        with col10:
            logo_transparency = st.number_input("🔅 Logo transparency (%)", min_value=0, max_value=100, value=default_values["logo_transparency"])
    else:
        logo_file = None
        logo_size_percentage = 0
        logo_transparency = 100

    # Validate file name
    if not file_name:
        st.error("❌ File name cannot be empty.")
        return

    # MIME type and file format mapping
    format_map = {
        'PNG': ('image/png', 'PNG'),
        'JPEG': ('image/jpeg', 'JPEG'),
        'JPG': ('image/jpeg', 'JPEG'),
        'WEBP': ('image/webp', 'WEBP'),
        'GIF': ('image/gif', 'GIF')
    }
    mime_type, file_format = format_map[file_type]

    st.success(f"✅ QR code successfully You can download your file as {file_name.lower()}.{file_type.lower()}")

    # Generate and display QR code
    qr_img = generate_qr_code(qr_type, data, color, bg_color, box_size, border, version, error_correction, include_logo, logo_file, logo_size_percentage, logo_transparency)
    if qr_img is None:
        return

    buffered = BytesIO()
    qr_img.save(buffered, format=file_format)
    qr_img_base64 = buffered.getvalue()

    st.image(qr_img_base64, use_column_width=True)

    # Download button for the QR code
    st.download_button(
        label="⬇️ Download QR Code",
        data=buffered.getvalue(),
        file_name=f"{file_name.lower()}.{file_type.lower()}",
        mime=mime_type
    )

if __name__ == "__main__":
    main()
