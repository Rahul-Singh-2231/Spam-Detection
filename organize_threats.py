import os
import pandas as pd
from feature_extractor import FeatureExtractor
from preprocessing import TextPreprocessor

# Custom high-quality templates to supplement categories that are sparse in the SMS dataset
CUSTOM_THREAT_SAMPLES = {
    'lottery_scam': [
        "Congratulations! Your mobile number has won $2,500,000.00 in the ongoing global lottery promotion. Claim code: G889. Contact claim agent at agent@promotions-mail.com",
        "DEAR WINNER, you have won £1,000,000 in the National Lottery Draw. Draw date: 14/07/2026. To file your claim, please reply with your name, phone number, and address.",
        "You are the lucky winner of a brand new BMW 3-Series and $500,000 cash prize! Send your winning number BMW-881 to bmwclaims@germany-mail.com to claim.",
        "Mega Million Jackpot: Your email was drawn for a reward of $10,000,000. Under safety laws, keep this confidential. Contact claims manager to process payouts."
    ],
    'banking_fraud': [
        "Alert: Unusual activity detected on your Chase debit card. A transaction of $450.00 at Target is pending. If this was not you, please verify your identity immediately: http://chase-security-update.net",
        "Wells Fargo Alert: Your online banking account has been temporarily disabled due to suspicious login attempts. Secure your account now at http://wellsfargo-verify-login.org",
        "HSBC security notice: A new device was linked to your online banking profile. If you did not authorize this change, please cancel it here: http://hsbc-device-authorization.com",
        "BOA Security: Your passcode was changed today. If you did not make this change, please call our 24/7 security line at 1-800-555-0199 immediately."
    ],
    'otp_fraud': [
        "Use 883921 as your Google Account recovery code. Do not share this OTP with anyone, including Google employees. If you did not request this, ignore this message.",
        "Security Code: Your Apple ID verification code is 299103. Never share your passcode or security codes with anyone.",
        "Your Instagram verification pin is 449281. Enter this to confirm your login. We will never call or message you to ask for this code.",
        "Bank OTP: Code 772910 is valid for 5 minutes to approve a transfer of $1,200.00. Never read this code to anyone over the phone."
    ],
    'crypto_scam': [
        "Binance Premium Airdrop: Claim 0.5 BTC instantly! Only available for the first 500 active users. Connect your MetaMask wallet at http://binance-free-airdrop.xyz",
        "Ethereum Foundation promotion: Send between 1 to 10 ETH to the contribution wallet below and get double (2 to 20 ETH) sent back to your address instantly!",
        "Crypto Alert: Join our Telegram signal group for guaranteed 1000% returns daily. Premium insights on altcoins and Bitcoin: http://t.me/crypto-signals-global",
        "TrustWallet Notice: Your wallet recovery phrase is expiring. Re-verify your seed phrase to prevent permanent loss of funds: http://trustwallet-security-phrase.net"
    ],
    'investment_scam': [
        "Earn up to 5% daily passive income with our AI-driven Forex trading algorithm. Fully licensed, guaranteed returns, low risk. Register today: http://highyield-investment.biz",
        "Guaranteed Stock Tip: Buy ticker symbol XYZ tomorrow at market open. Target gains +400% in 1 week. Join our premium advisory network for daily targets.",
        "Retire early! Invest just $100 in our silver trading program and watch it grow to $10,000 in 3 months. No experience required: http://silver-growth-funds.com"
    ],
    'job_scam': [
        "We are hiring remote data entry assistants! Work 2-3 hours per day from home and earn $30-$50 per hour. Weekly payouts via wire transfer. Apply now: jobs@remote-career-hub.com",
        "Job Offer: Your resume was approved for the position of Logistics Manager. Salary: $5,000/month. Please review the offer letter and details at http://global-logistics-careers.com",
        "Earn money by reviewing apps! Looking for 15 workers in your area. Salary up to $300/day. No experience needed. Contact coordinator via WhatsApp: +1234567890"
    ],
    'delivery_scam': [
        "USPS Update: Your parcel could not be delivered due to an incorrect house number. Please update your address and pay the $1.50 redelivery fee: http://usps-redelivery-tracking.info",
        "DHL Express: Your package #DHL-39829 is held at our local sorting hub due to unpaid customs duties of $2.40. Settle the fee online to resume dispatch: http://dhl-customs-payment.com",
        "FedEx Notification: Shipment tracking status changed to PENDING. Resolve outstanding shipping address issues to avoid return to sender: http://fedex-update-package.net"
    ],
    'govt_impersonation': [
        "Internal Revenue Service: You have an outstanding tax refund of $820.00 waiting to be processed. Fill out form 1040-EZ online to claim your refund: http://irs-refund-portal.gov-tax.net",
        "Social Security Administration Alert: Your SSN has been suspended due to suspected fraudulent activity in Texas. Call our legal department immediately at 1-888-555-0122.",
        "Medicare Notice: Confirm your eligibility and update your profile to receive the new Medicare smart card. Failure to update will result in suspension of benefits: http://medicare-card-update.org"
    ],
    'tech_support_scam': [
        "WARNING: Microsoft Security Alert! Your computer is infected with Trojan malware (v2.89). Your personal data, passwords, and banking details are at risk. Call toll-free immediately: 1-800-555-0144",
        "Apple Support: Unauthorized access detected on your iCloud backup from an IP address in Russia. Call Apple tech line at 1-877-555-0177 to secure your Apple ID.",
        "Firewall Warning: Windows Defender has blocked an unauthorized connection attempt. System scan shows 14 critical threats. Contact Microsoft support engineers at http://defender-helpdesk.online"
    ],
    'gmail_phishing': [
        "Gmail Security: Your account was accessed from a new browser in Russia. If this was not you, reset your password immediately to prevent lockout: http://gmail-security-account.com",
        "Google Workspace Alert: Your storage is full (100% of 15GB). Incoming emails are being bounced. Upgrade or verify your billing details: http://google-storage-upgrade.com",
        "Important Notification: Access to your Google accounts will be suspended within 24 hours due to violations of Terms of Service. Click here to appeal: http://google-account-verify.net"
    ]
}

def organize_threat_dataset():
    tsv_path = os.path.join('dataset', 'SMSSpamCollection.tsv')
    if not os.path.exists(tsv_path):
        print(f"Error: Dataset not found at {tsv_path}. Run train_model.py first.")
        return

    print("============================================================")
    print("  THREAT DATASET ORGANIZER")
    print("============================================================")

    # Initialize extractor & preprocessor
    extractor = FeatureExtractor()
    preprocessor = TextPreprocessor()

    # Load TSV
    df = pd.read_csv(tsv_path, sep='\t', header=None, names=['label', 'message'], encoding='latin-1')

    # Define base output directory
    base_dir = os.path.join('dataset', 'threats')
    os.makedirs(base_dir, exist_ok=True)

    # Folders dictionary mapping category key to folder name
    categories = {
        'lottery_scam': 'lottery_scams',
        'banking_fraud': 'banking_fraud',
        'otp_fraud': 'otp_fraud',
        'crypto_scam': 'crypto_scams',
        'investment_scam': 'investment_scams',
        'job_scam': 'job_scams',
        'delivery_scam': 'delivery_scams',
        'govt_impersonation': 'govt_impersonation',
        'tech_support_scam': 'tech_support_scams',
        'gmail_phishing': 'gmail_phishing',
        'legitimate_ham': 'legitimate_ham'
    }

    # Create directories
    for folder in categories.values():
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

    counts = {k: 0 for k in categories.keys()}
    records = []

    # Process and organize SMS dataset messages
    print("Processing and categorizing SMS messages...")
    for idx, row in df.iterrows():
        label = row['label']
        message = row['message'].strip()
        
        if not message:
            continue

        if label == 'ham':
            # Save normal messages in legitimate_ham folder
            folder_name = categories['legitimate_ham']
            counts['legitimate_ham'] += 1
            file_name = f"ham_{counts['legitimate_ham']:04d}.txt"
            with open(os.path.join(base_dir, folder_name, file_name), 'w', encoding='utf-8') as f:
                f.write(message)
            records.append({
                'message': message,
                'label': 'ham',
                'threat_category': 'legitimate_ham'
            })
        else:
            # For spam, detect specific threat categories
            # Preprocess to get clean tokens
            prep = preprocessor.preprocess(message)
            features = extractor.extract_features(message, prep)
            threats = features['detected_threats']

            # Check for email/gmail specific keywords to place in gmail_phishing
            is_gmail_phishing = any(x in message.lower() for x in ['gmail', 'google', 'outlook', 'yahoo', 'email', 'inbox'])
            
            if is_gmail_phishing and ('password' in message.lower() or 'login' in message.lower() or 'verify' in message.lower() or 'link' in message.lower()):
                assigned_category = 'gmail_phishing'
            elif threats:
                # Assign to the first detected threat category
                assigned_category = threats[0]
            else:
                # Fallback to general spam / phishing
                # Check for generic phishing words
                phishing_words_found = extractor._find_matching_words(message.lower(), extractor.PHISHING_WORDS)
                if phishing_words_found:
                    assigned_category = 'gmail_phishing'
                else:
                    assigned_category = 'lottery_scam' # fallback default spam folder

            folder_name = categories[assigned_category]
            counts[assigned_category] += 1
            file_name = f"spam_{counts[assigned_category]:04d}.txt"
            with open(os.path.join(base_dir, folder_name, file_name), 'w', encoding='utf-8') as f:
                f.write(message)
            records.append({
                'message': message,
                'label': 'spam',
                'threat_category': assigned_category
            })

    # Process and inject custom templates to ensure all folders have high quality structured threat files
    print("Injecting high-quality custom threat templates...")
    for category, templates in CUSTOM_THREAT_SAMPLES.items():
        folder_name = categories[category]
        for template in templates:
            counts[category] += 1
            file_name = f"template_{counts[category]:04d}.txt"
            with open(os.path.join(base_dir, folder_name, file_name), 'w', encoding='utf-8') as f:
                f.write(template)
            records.append({
                'message': template,
                'label': 'spam',
                'threat_category': category
            })

    # Export consolidated file
    print("Saving consolidated threat datasets...")
    consolidated_df = pd.DataFrame(records)
    csv_out = os.path.join('dataset', 'consolidated_threats.csv')
    json_out = os.path.join('dataset', 'consolidated_threats.json')
    
    consolidated_df.to_csv(csv_out, index=False, encoding='utf-8')
    consolidated_df.to_json(json_out, orient='records', indent=2, force_ascii=False)

    print("\n============================================================")
    print("  ORGANIZATION SUMMARY")
    print("============================================================")
    for cat_key, folder in categories.items():
        print(f"  Folder: {folder.ljust(22)} | Files created: {counts[cat_key]}")
    print("============================================================")
    print(f"Dataset successfully created and sorted under: {base_dir}")
    print(f"Consolidated CSV saved: {csv_out}")
    print(f"Consolidated JSON saved: {json_out}")

if __name__ == '__main__':
    organize_threat_dataset()
