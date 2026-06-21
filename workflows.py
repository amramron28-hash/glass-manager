    # 🟡 الخطة 2 & 3: الهاتف غير مدرج - حقن كروت نيون زجاجية منفصلة ومتقطعة تناسب هندسة النظام الموحد
    elif phone:
        # الخطة 2: كارت نيون زجاجي أزرق فاخر لمعالجة الـ API
        html_output.append(f"""
            <div style="font-size: 20px !important; font-weight: bold !important; color: #ffffff !important; margin-top: 25px !important; margin-bottom: 12px !important; text-align: right !important; direction: rtl !important;">
                <span style="color:#00bfff; margin-left: 6px;">🔍</span>حالة معالجة وفحص الموديل:
            </div>
            <div class="ammar-flat-card" style="background: linear-gradient(135deg, #0b1a33, #060e1c) !important; border: 2px solid #00bfff !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: ltr !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(0, 191, 255, 0.25) !important; box-sizing: border-box !important;">
                <div style="color: #ffffff !important; font-size: 21px !important; font-weight: 800 !important; text-align: left !important; margin: 0 !important;">جاري معالجة ومطابقة: {escape(phone)}</div>
            </div>
        """)
        
        ai_result = ai_background_global_verify(phone)
        if ai_result:
            # نتائج الفحص العالمي في كارت نيون فيروزي فخم ومستقل تماماً
            html_output.append(f"""
                <div class="ammar-flat-card" style="background: linear-gradient(135deg, #071f21, #030f10) !important; border: 2px solid #00ffcc !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: ltr !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(0, 255, 204, 0.25) !important; box-sizing: border-box !important;">
                    <div style="color: #00ffcc !important; font-size: 19px !important; font-weight: 800 !important; text-align: left !important; direction: rtl !important; width:100%;">
                        🤖 <b>نتائج الفحص العالمي الذكي:</b><br>
                        📏 الحجم المتوقع: {escape(ai_result['size'])} | 📺 الشاشة: {escape(ai_result['panel'])} | 🔌 الحساس: {escape(ai_result['sensor'])}
                    </div>
                </div>
            """)
        else:
            # الخطة 3 (خطة الطوارئ): كارت نيون برتقالي مضيء منفصل ومتقطع 100% ومطابق لحجم كروتك
            html_output.append(f"""
                <div style="font-size: 20px !important; font-weight: bold !important; color: #ffffff !important; margin-top: 25px !important; margin-bottom: 12px !important; text-align: right !important; direction: rtl !important;">
                    <span style="color:#ff4500; margin-left: 6px;">⚠️</span>تنبيه النظام الموحد لعدم الإدراج:
                </div>
                <div class="flat-warning-card" style="background: linear-gradient(135deg, #26090b, #120405) !important; border: 2px solid #ff4500 !important; padding: 16px 20px !important; margin-bottom: 14px !important; border-radius: 12px !important; display: flex !important; align-items: center !important; justify-content: space-between !important; direction: rtl !important; width: 100% !important; box-shadow: 0px 4px 12px rgba(255, 69, 0, 0.3) !important; box-sizing: border-box !important;">
                    <div style="color: #ffb3b9 !important; font-size: 20px !important; font-weight: 700 !important; text-align: right !important; line-height: 1.5; width:100%;">
                        الموديل غير مدرج حالياً. يمكنك استخدام نموذج الإدخال اليدوي بأسفل لوحة التحكم لتوثيقه وضخه في قاعدة بيانات النظام.
                    </div>
                </div>
            """)

    return "\n".join(html_output)
