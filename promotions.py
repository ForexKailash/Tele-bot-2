import random

# ------------------------------------------------------------
# 30+ FOMO‑Driven, Creative Promotional Messages (Indian English)
# ------------------------------------------------------------

def get_hype_promo(channel_link, vip_link, contact, upi, course_url):
    messages = [
        # 1. Urgency + Limited slots
        f"⚠️ *ONLY {random.randint(2,5)} VIP SEATS LEFT!* ⚠️\n\nNext price ₹599. Lock ₹399 forever.\n\n👉 {vip_link}",

        # 2. Social proof + Profit
        f"💸 *Just 10 minutes ago:* A VIP member booked ₹8,200 profit on GOLD.\n\nYou missed it because you're not VIP.\n\nJoin now: {vip_link}",

        # 3. Fear of missing tomorrow's big move
        f"🚨 *TOMORROW'S BIG NEWS:* NFP data coming.\n\nVIP members will get early entry 30 mins before the spike.\n\nDon't be late. Join: {vip_link}",

        # 4. Countdown style
        f"⏳ *DEADLINE:* Midnight tonight – VIP price increases to ₹599.\n\n{random.randint(3,6)} people already upgraded today.\n\nLock ₹399: {vip_link}",

        # 5. Direct comparison with free channel
        f"📢 *FREE CHANNEL:* Signal delayed by 30 minutes.\n\nVIP members already booked TP1.\n\nStop chasing. Start leading.\n👉 {vip_link}",

        # 6. Testimonial with numbers
        f"⭐ *VIP MEMBER REVIEW:* \"Made 1.2 lakh in first month. Best ₹399 I ever spent.\" – Vikram, Delhi\n\nYou're next? Join: {vip_link}",

        # 7. Loss aversion
        f"💔 *Yesterday's GOLD move:* +450 pips.\n\nVIP members caught it from the bottom.\n\nFree channel got signal after 250 pips.\n\nDon't lose again: {vip_link}",

        # 8. Flash sale
        f"🔥 *FLASH SALE:* First 5 new VIPs today get FREE Forex Masterclass (₹2,999 value).\n\nAlready 3 claimed. Hurry!\n\n{vip_link}",

        # 9. Insider info
        f"🤫 *INSIDER TIP:* A big bank order just detected on BTC.\n\nVIP members will get the exact entry in 20 mins.\n\nBe ready: {vip_link}",

        # 10. Scarcity + social proof
        f"📊 *Last month:* 342 traders joined VIP.\n\nThis month only 87 slots left.\n\nDon't be the one who regrets.\n👉 {vip_link}",

        # 11. Question to trigger FOMO
        f"❓ *Why are you still watching?*\n\nVIP members are making money while you read this.\n\n₹399 is less than one pizza.\n\nJoin the winning side: {vip_link}",

        # 12. Bold claim
        f"🏆 *89% WIN RATE* – Not a guess. Proof in every signal.\n\nFree channel sees the result. VIP gets the result first.\n\nUpgrade now: {vip_link}",

        # 13. Actionable urgency
        f"⚡ *NEXT VIP SIGNAL IN 10 MINUTES* – on GOLD.\n\nEntry will be sent ONLY to VIP channel.\n\nIf you're not there, you'll miss.\n\nJoin instantly: {vip_link}",

        # 14. Fear of being left behind
        f"👀 *Look who just joined VIP:* @traderrahul and @forexanita.\n\nYour competitors are getting ahead.\n\nDon't be left behind.\n👉 {vip_link}",

        # 15. Benefit stacking
        f"🎁 *What ₹399 gets you:*\n✅ 30-35 premium signals/month\n✅ Early entry (30 min before free)\n✅ Live market analysis\n✅ 1-on-1 support\n✅ Copy trade setup help\n\nThat's less than ₹13/day.\n\nJoin: {vip_link}",

        # 16. FOMO from past wins
        f"💰 *THIS WEEK'S VIP PROFITS:*\n📈 GOLD: +320 pips\n📈 BTC: +$2,400\n📈 EUR/USD: +180 pips\n\nTotal = ₹28,000+ for members.\n\nYou missed all. Why?\n👉 {vip_link}",

        # 17. Low risk, high reward
        f"💎 *Risk ₹399 to make ₹15,000+* – that's 3,600% ROI.\n\nWould you take that trade?\n\nThen take this offer.\n\n{vip_link}",

        # 18. Time decay
        f"⏰ *This offer expires in 2 hours.*\n\nAfter that, VIP price goes to ₹599.\n\n{random.randint(4,8)} people are viewing this now.\n\nSecure your spot: {vip_link}",

        # 19. Celebrity endorsement style
        f"🌟 *\"I've tried 10+ signal groups. Kailash is the only one that delivers.\"* – Ankit, IITian turned trader.\n\nJoin the smart money: {vip_link}",

        # 20. Direct challenge
        f"🎯 *Challenge:* Take 3 free signals. If they don't impress you, don't join VIP.\n\nBut if they do, you're losing money by waiting.\n\nFree channel: {channel_link}\nVIP: {vip_link}",

        # 21. Scarcity of time
        f"🕐 *Market opens in 1 hour.*\n\nVIP members will get the first signal at 7:00 AM IST.\n\nFree channel at 7:30 AM.\n\n30 minutes = 30% more profit.\n\nJoin now: {vip_link}",

        # 22. Visual urgency
        f"🔴 *LAST CALL* 🔴\n\nVIP slots remaining: {random.randint(2,4)}\n\nPrice after filling: ₹599\n\n👉 {vip_link}",

        # 23. Social proof + immediate action
        f"📢 *BREAKING:* 5 new VIP members joined in last 30 minutes.\n\nThey saw the GOLD signal and didn't hesitate.\n\nWill you be the 6th?\n\n{vip_link}",

        # 24. Pain of missing
        f"😭 *\"I was about to join VIP last week, but I didn't. Missed 3 TP2 hits.\"* –的真实 user.\n\nDon't let that be you.\n\nJoin today: {vip_link}",

        # 25. Bonus urgency
        f"🎁 *BONUS:* First 10 VIPs today get FREE access to my ₹2,999 Forex Course.\n\n{random.randint(5,8)} already claimed.\n\nOnly {random.randint(2,5)} left.\n\n{vip_link}",

        # 26. Market volatility
        f"🌪️ *MARKET ALERT:* High volatility expected in next 2 hours (US session).\n\nVIP members will get real‑time updates and entry levels.\n\nDon't trade blind.\n👉 {vip_link}",

        # 27. Simple math
        f"🧮 *Simple math:* ₹399 ÷ 30 days = ₹13.3/day.\n\nOne good trade pays for 10 months of VIP.\n\nStill thinking?\n\n{vip_link}",

        # 28. Fear of being average
        f"📉 *90% of retail traders lose money.*\n\nVIP members are in the top 10% because they follow a system.\n\nWhich group do you want to be in?\n\n{vip_link}",

        # 29. Exclusive access
        f"🔑 *VIP EXCLUSIVE:* Tomorrow's high‑probability setup on NAS100.\n\nOnly VIP members will see the entry before the move.\n\nGet the key: {vip_link}",

        # 30. Personal invitation
        f"💌 *Personal invitation from Kailash:*\n\nI want you to be part of my winning team.\n\nBut I can't hold the ₹399 price forever.\n\nJoin me inside VIP: {vip_link}",

        # 31. Real‑time proof
        f"📡 *LIVE:* A VIP signal just hit TP2 on US30. +180 points.\n\nCheck the public channel in 30 minutes – you'll see the result.\n\nWhy wait? Join VIP: {vip_link}",

        # 32. Double urgency
        f"🔥 *2 REASONS TO JOIN NOW:*\n1. Price increases tomorrow (₹399 → ₹599)\n2. First signal in 15 minutes (GOLD)\n\nDon't miss both.\n\n{vip_link}",
    ]
    return random.choice(messages)
