/* =========================================
   ZEGAAR AMMAR GLASS MANAGER UI
========================================= */

html, body, .container-fluid{
    background-color:#0a0e17 !important;
    color:white !important;
    direction:rtl !important;
    font-family:"Segoe UI",sans-serif !important;
}

body{
    background-image:
        linear-gradient(
            rgba(10,14,23,.20),
            rgba(10,14,23,.20)
        ),
        url('/phone_image.webp') !important;

    background-size:92% auto !important;
    background-position:center center !important;
    background-repeat:no-repeat !important;
    background-attachment:fixed !important;
}

/* =========================================
   HEADER
========================================= */

.header-bar{
    display:flex;
    justify-content:space-between;
    align-items:center;

    padding:12px 25px;

    background:rgba(13,17,23,.55);

    backdrop-filter:blur(12px);

    border-bottom:
    1px solid rgba(0,191,255,.25);
}

.brand-neon-title{
    text-align:right;
    line-height:1.05;
}

.brand-neon-main{
    color:#00bfff;
    font-size:30px;
    font-weight:900;

    text-shadow:
    0 0 5px rgba(0,191,255,.7),
    0 0 15px rgba(0,191,255,.5);
}

.brand-neon-sub{
    color:#87ceeb;

    font-size:18px;

    font-weight:700;

    letter-spacing:4px;

    text-shadow:
    0 0 5px rgba(135,206,235,.6);
}

/* =========================================
   SEARCH
========================================= */

.search-box{
    position:relative;
    width:90%;
    max-width:500px;
    margin:30px auto;
}

input[type="text"]{

    width:100% !important;

    background:
    rgba(17,24,39,.90)!important;

    color:white!important;

    border:
    1px solid #00bfff!important;

    border-radius:14px!important;

    padding:14px!important;

    box-shadow:
    0 0 15px rgba(0,191,255,.15)!important;

    direction:ltr!important;

    text-align:left!important;
}

/* =========================================
   AUTOCOMPLETE
========================================= */

.suggestions-curtain{

    position:absolute;

    top:60px;

    right:0;
    left:0;

    background:
    rgba(22,27,34,.96);

    border:
    1px solid #00bfff;

    border-radius:12px;

    max-height:240px;

    overflow-y:auto;

    z-index:99999;

    backdrop-filter:blur(15px);

    box-shadow:
    0 8px 30px rgba(0,0,0,.6);
}

.suggestion-row{

    padding:12px;

    color:white;

    cursor:pointer;

    border-bottom:
    1px solid rgba(255,255,255,.08);

    direction:ltr;

    text-align:left;
}

.suggestion-row:hover{

    background:
    rgba(0,191,255,.18);
}

/* =========================================
   GLASS CARD
========================================= */

.glass-card{

    background:
    rgba(255,255,255,.06);

    backdrop-filter:
    blur(15px);

    border:
    1px solid rgba(0,191,255,.35);

    border-radius:20px;

    padding:20px;

    margin:20px auto;

    max-width:500px;
}

/* =========================================
   RESULT CARDS
========================================= */

.ammar-flat-card{

    display:flex;

    align-items:center;

    justify-content:flex-end;

    padding:16px 24px;

    margin-bottom:14px;

    border-radius:24px;

    width:100%;

    position:relative;

    overflow:hidden;
}

.flat-exact{

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,.30) 0%,
        rgba(76,187,85,.45) 50%,
        rgba(34,111,41,.60) 100%
    );

    border:1px solid rgba(255,255,255,.4);

    box-shadow:
    inset 0 0 15px rgba(255,255,255,.5),
    0 8px 32px rgba(0,0,0,.1);

    backdrop-filter:blur(1px);
}

.flat-plus{

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,.30) 0%,
        rgba(41,98,255,.50) 50%,
        rgba(13,50,163,.60) 100%
    );

    border:1px solid rgba(255,255,255,.4);

    box-shadow:
    inset 0 0 15px rgba(255,255,255,.5),
    0 8px 32px rgba(0,0,0,.1);

    backdrop-filter:blur(1px);
}

.flat-minus{

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,.30) 0%,
        rgba(255,165,0,.45) 50%,
        rgba(230,126,34,.60) 100%
    );

    border:1px solid rgba(255,255,255,.4);

    box-shadow:
    inset 0 0 15px rgba(255,255,255,.5),
    0 8px 32px rgba(0,0,0,.1);

    backdrop-filter:blur(1px);
}

.flat-warning-card{

    background:
    linear-gradient(
        135deg,
        rgba(255,255,255,.30) 0%,
        rgba(255,82,82,.45) 50%,
        rgba(183,28,28,.60) 100%
    );

    border:1px solid rgba(255,255,255,.4);

    box-shadow:
    inset 0 0 15px rgba(255,255,255,.5),
    0 8px 32px rgba(0,0,0,.1);

    backdrop-filter:blur(1px);
}

.flat-phone-text{

    color:white;

    font-size:20px;

    font-weight:800;

    width:100%;

    text-align:left!important;

    direction:ltr!important;
}

/* =========================================
   DRAWER
========================================= */

.drawer{

    position:fixed;

    top:0;

    right:-320px;

    width:290px;

    height:100%;

    background:
    rgba(22,27,34,.95);

    backdrop-filter:
    blur(20px);

    border-left:
    2px solid #00bfff;

    transition:.4s;

    z-index:200000;

    padding:30px;
}

.drawer.open{
    right:0;
}

.metric-box{

    background:
    rgba(255,255,255,.05);

    padding:10px;

    border-radius:8px;

    margin-bottom:10px;

    text-align:center;

    border:
    1px solid rgba(0,191,255,.2);
}
