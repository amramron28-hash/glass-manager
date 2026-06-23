import re
import requests
from html import escape



def extract_numeric_size(size_string):

    try:

        match = re.search(
            r"[-+]?\d*\.\d+|\d+",
            str(size_string)
        )

        if match:

            return float(match.group())


    except Exception:

        pass


    return None






def find_model_coords(db_data, phone_name):


    if not phone_name or not db_data:

        return None, None, None, None



    search = str(phone_name).strip().lower()



    # تطابق كامل

    for size, panels in db_data.items():


        if not isinstance(panels, dict):

            continue



        for panel, sensors in panels.items():


            if not isinstance(sensors, dict):

                continue



            for sensor, data in sensors.items():


                models = []


                if isinstance(data, dict):

                    models = data.get("models", [])



                for model in models:


                    if str(model).strip().lower() == search:


                        return (
                            size,
                            panel,
                            sensor,
                            model
                        )





    # تطابق جزئي


    for size, panels in db_data.items():


        if not isinstance(panels, dict):

            continue



        for panel, sensors in panels.items():


            if not isinstance(sensors, dict):

                continue



            for sensor, data in sensors.items():


                models = []


                if isinstance(data, dict):

                    models=data.get("models",[])



                for model in models:


                    if search in str(model).lower():


                        return (
                            size,
                            panel,
                            sensor,
                            model
                        )



    return None,None,None,None







def get_compatibles_strict(db_data, phone_name):


    result = {

        "exact":[],
        "plus":[],
        "minus":[]

    }



    size,panel,sensor,real_name = find_model_coords(
        db_data,
        phone_name
    )



    if not size:

        return result



    current = extract_numeric_size(size)



    if current is None:

        return result



    tolerance = 0.03





    for size_key, panels in db_data.items():


        other = extract_numeric_size(size_key)


        if other is None:

            continue



        diff = other-current



        if not isinstance(panels,dict):

            continue





        for panel_key,sensors in panels.items():


            if panel_key != panel:

                continue



            for sensor_key,data in sensors.items():


                if sensor_key != sensor:

                    continue



                models=[]


                if isinstance(data,dict):

                    models=data.get(
                        "models",
                        []
                    )



                for model in models:


                    if str(model).lower() == str(real_name).lower():

                        continue





                    if abs(diff) < 0.001:


                        if model not in result["exact"]:

                            result["exact"].append(model)



                    elif 0 < diff <= tolerance:


                        if model not in result["plus"]:

                            result["plus"].append(model)



                    elif -tolerance <= diff < 0:


                        if model not in result["minus"]:

                            result["minus"].append(model)




    return result








def ai_background_global_verify(phone_name):


    try:


        url = (
            "https://example.com/api/"
            +
            requests.utils.quote(
                str(phone_name)
            )
        )


        r = requests.get(
            url,
            timeout=2
        )



        if r.status_code == 200:


            data=r.json()


            return {


                "size":str(
                    data.get(
                        "size",
                        "غير محدد"
                    )
                ),


                "panel":str(
                    data.get(
                        "panel",
                        "غير محدد"
                    )
                ),


                "sensor":str(
                    data.get(
                        "sensor",
                        "غير محدد"
                    )
                )

            }



    except Exception:

        pass



    return None








def run_system_workflows(
    phone,
    db_data,
    suggestions=None
):


    from ui_components import (
        draw_technical_coords,
        draw_neon_section
    )



    if not phone:

        return ""



    size,panel,sensor,real_name = find_model_coords(
        db_data,
        phone
    )



    output=[]





    if real_name:



        output.append(

            str(

                draw_technical_coords(

                    size,
                    panel,
                    sensor,
                    real_name

                )

            )

        )





        compatible=get_compatibles_strict(
            db_data,
            phone
        )





        output.append(

            str(

                draw_neon_section(

                    "مطابقة تماماً",

                    compatible["exact"],

                    "#2ecc71",

                    "🟢"

                )

            )

        )





        output.append(

            str(

                draw_neon_section(

                    "أكبر قليلاً",

                    compatible["plus"],

                    "#3498db",

                    "🔵"

                )

            )

        )





        output.append(

            str(

                draw_neon_section(

                    "أصغر قليلاً",

                    compatible["minus"],

                    "#e67e22",

                    "🟠"

                )

            )

        )





    else:



        output.append(

            """

<div class="flat-warning-card">

⚠️ الموديل غير موجود في قاعدة البيانات

</div>

"""

        )




        ai=ai_background_global_verify(phone)



        if ai:


            output.append(

                f"""

<div class="glass-card">

🤖 الفحص الذكي

<br>

📏 {escape(ai['size'])}

<br>

📺 {escape(ai['panel'])}

<br>

👁️ {escape(ai['sensor'])}

</div>

"""

            )





    return "\n".join(output)
