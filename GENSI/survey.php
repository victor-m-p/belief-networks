<?php header("Content-Type: text/html; charset=utf-8"); ?>

<!DOCTYPE html>
<html>
  <head>
    <title></title>
    <meta content="text/html;charset=utf-8" http-equiv="Content-Type">
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet"> 
    <!--<link rel="stylesheet" href="bootstrap.min.css">-->
    <script src="jquery.min.js"></script>
  </head>
  <body>
    <script src="d3.v3.min.js" charset="utf-8"></script>
    <script src="jquery-1.11.0.js"></script>
    <script type="text/javascript">

      const queryString = window.location.search;
      const urlParams = new URLSearchParams(queryString);
      

      // Prevent window close
      var hook = true;
      window.onbeforeunload = function() {
        if (hook) {       
          return "Are you sure that you want to end this survey? All of your answers will be lost.";
        }
      }
      function unhook() {
        hook=false;
      }
      var in_between_0 = Math.floor(Math.random() * 3);
      
      console.log(in_between_0);
      

      var bodyWidth = $(document).width();
      var bodyHeight = $(document).height() - 20;
      if (bodyWidth < 800) bodyWidth = 800;
      if (bodyHeight < 750) bodyHeight = 750;
      var center = bodyWidth / 2;
      var middle = bodyHeight / 200;
      
      var textWidth = 800;
      // var textWidth = .8 * bodyWidth;
      var keys = [];

      var text_offset_top = 180;
      var title_offset_top = 70;
      var lineHeight = 26;
      var nodeLine = 520;
      
      var q_window_width = 100,
          q_window_height = 100,
          backdrop_width = 500;

      // left and top values for individual questions
      var question_lnum = center - (textWidth / 2);
      var string_l = question_lnum.toString();
      var string_t = "150px";
      var string_radio = "250px";
      var string_r_t = "45%",
          q_margin_top = 200,
          q_margin_top_str = q_margin_top.toString();

      // bar with boxes for answers
      var boxbar_margin = 10,
          boxbar_label_margin = 3,
          bar_target_height = 100,
          bar_target_width = ((bodyWidth - (boxbar_margin * 4) - 20) / 5),
          bar3_target_width = ((bodyWidth - (boxbar_margin * 2) - 20) / 3),
          bar4_target_width = ((bodyWidth - (boxbar_margin * 3) - 20) / 4),
          bar5_target_width = ((bodyWidth - (boxbar_margin * 4) - 20) / 5),
          bar6_target_width = ((bodyWidth - (boxbar_margin * 5) - 20) / 6),
          bar_label_height = 25,
          boxbar_offset_x = 10,
          boxbar_offset_y = bodyHeight - bar_target_height;

      var currSlide = 0;
      var currQuestion = 1;
      var numAlters = 0;
      var askedAbout = 0;
      var lastAskedAbout = 0;
      var numAsked = 1;
      var lastAnswered = 0;
      var numOther = 0;
      var checked = false;
      var altered = false;
      var skipped = false;
      var currNode = null;
      var nodeColor = '#9CD4D4',
          selfColor = '#589191'
          maleColor = '#a8a4ff',
          friendsColor = '#42f477',
          kidsColor = '#ffc1d8',
          kinderwensColor = '#ce88ae',
          kinderloosColor = '#c0d183',
          kinderhulpColor = '#c8b6db',
          kinderpraatColor = '#ef8f8f',
          answerColor = '#abff48',
          answerColors = ['#ffffff', '#c4f1be', '#a2c3a4', '#869D96', '#525b76', '#999'];

          

      var startTime;
      var answers = [];
    </script>
    <script src="ie.js"></script>
    <script src="nodefunctions.js"></script>
    <script src="graph.js"></script>
    <script src="elementmanipulation.js"></script>    
    <script src="slides.js"></script>
    <script src="multiplechoiceelements.js"></script>
    <script src="shownext.js"></script>
    <script src="keypress.js"></script>

    <div class="header"><img src="Universiteit_Utrecht_Logo.png" alt="Universiteit Utrecht" class="logo" /></div>

    <div class="input-group radio_slide" display="none" id="self_strictness" method="get">
      <form id="self_strictness_form" display="none">
        <span class="slideText" style="">Hoe strikt houdt u zich op dit moment aan de coronamaatregelen van de regering? </span><br><br>
        <div class="radio" onclick="$('#self_strictness_radio_0').prop('checked', true)"><label class="container"><input type="radio" id="self_strictness_radio_0" name="self_strictness_radio" value=1><span class="checkmark"></span></label><span class="questionText">Helemaal niet</span></div>
        <div class="radio" onclick="$('#self_strictness_radio_1').prop('checked', true)"><label class="container"><input type="radio" id="self_strictness_radio_1" name="self_strictness_radio" value=2><span class="checkmark"></span></label><span class="questionText">  Een beetje</span></div>
        <div class="radio" onclick="$('#self_strictness_radio_2').prop('checked', true)"><label class="container"><input type="radio" id="self_strictness_radio_2" name="self_strictness_radio" value=3><span class="checkmark"></span></label><span class="questionText">  Best wel</span></div>
        <div class="radio" onclick="$('#self_strictness_radio_3').prop('checked', true)"><label class="container"><input type="radio" id="self_strictness_radio_3" name="self_strictness_radio" value=4><span class="checkmark"></span></label><span class="questionText">  Strikt</span></div>
        <div class="radio" onclick="$('#self_strictness_radio_4').prop('checked', true)"><label class="container"><input type="radio" id="self_strictness_radio_4" name="self_strictness_radio" value=5><span class="checkmark"></span></label><span class="questionText">  Heel strikt</span></div>
      </form>
    </div>


    <div class="input-group radio_slide" display="none" id="slide23_0" method="get">
      <span class="slideText" style="">Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine moet gaan. U heeft echter geen klachten. Hoe waarschijnlijk is het dat u in quarantaine zult gaan? </span><br><br>
    </div>
    <div class="input-group radio_slide" display="none" id="slide23_1" method="get">
      <span class="slideText" style="">Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine moet gaan. U heeft echter geen klachten. Goede vrienden van u vinden dat u alsnog in thuisquarantaine behoort te gaan. Hoe waarschijnlijk is het dat u in quarantaine zult gaan? </span><br><br>
    </div>
    <div class="input-group radio_slide" display="none" id="slide23_2" method="get">
      <span class="slideText" style="">Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine moet gaan. U heeft echter geen klachten. Goede vrienden vinden dat u dan ook niet in thuisquarantaine behoort te gaan. Hoe waarschijnlijk is het dat u in quarantaine zult gaan?</span><br><br>
    </div>
    <div class="input-group radio_slide" display="none" id="slide23" method="get" style="">
      <form id="between_subject_radio_0" display="none">
        <span class="slideText">  </span><br><br>
        <div class="radio" onclick="$('#between_subject_radio_0_0').prop('checked', true)"><label class="container"><input type="radio" id="between_subject_radio_0_0" name="between_subject_radio_0" value=1><span class="checkmark"></span></label><span class="questionText">  Helemaal niet waarschijnlijk</span></div>
        <div class="radio" onclick="$('#between_subject_radio_0_1').prop('checked', true)"><label class="container"><input type="radio" id="between_subject_radio_0_1" name="between_subject_radio_0" value=2><span class="checkmark"></span></label><span class="questionText">  Niet waarschijnlijk</span></div>
        <div class="radio" onclick="$('#between_subject_radio_0_2').prop('checked', true)"><label class="container"><input type="radio" id="between_subject_radio_0_2" name="between_subject_radio_0" value=3><span class="checkmark"></span></label><span class="questionText">  Best wel waarschijnlijk</span></div>
        <div class="radio" onclick="$('#between_subject_radio_0_3').prop('checked', true)"><label class="container"><input type="radio" id="between_subject_radio_0_3" name="between_subject_radio_0" value=4><span class="checkmark"></span></label><span class="questionText">  Waarschijnlijk</span></div>
        <div class="radio" onclick="$('#between_subject_radio_0_4').prop('checked', true)"><label class="container"><input type="radio" id="between_subject_radio_0_4" name="between_subject_radio_0" value=5><span class="checkmark"></span></label><span class="questionText">  Heel waarschijnlijk</span></div>
      </form>
    </div>



    <div class="input-group radio_slide" display="none" id="slide24_0" method="get">
        <span class="slideText" style="">Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt daarom of het wel verstandig is om naar de verjaardag te gaan. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan? </span><br><br>
    </div>
    <div class="input-group radio_slide" display="none" id="slide24_1" method="get">
        <span class="slideText" style="">Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt daarom of het wel verstandig is om naar de verjaardag te gaan. Goede vrienden van u hebben besloten om niet naar de verjaardag te gaan. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan?</span><br><br>
    </div>
    <div class="input-group radio_slide" display="none" id="slide24_2" method="get">
        <span class="slideText" style="">Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt daarom of het wel verstandig is om naar de verjaardag te gaan. Goede vrienden van u gaan echter wel naar de verjaardag. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan?</span><br><br>
    </div>

    <div class="input-group" display="none" id="moral_obligations" method="get">
      <table class = 'questionTable'>
        <thead>
          <tr>
            <td width = "25%">   </td>
            <th width = "15%" class = "tableHeaderValues"> Helemaal oneens </th>
            <th width = "15%" class = "tableHeaderValues"> Oneens </th>
            <th width = "15%" class = "tableHeaderValues"> Een beetje eens </th>
            <th width = "15%" class = "tableHeaderValues"> Eens </th>
            <th width = "15%" class = "tableHeaderValues"> Helemaal eens </th>
          </tr>
        </thead>
        <tbody>
          
          <tr class="radio">
            <span class="slideText" style="width: 60%;">Bent u het eens of oneens met de volgende uitspraken?</span><br><br><br>

            <form id = "tableRow1">
              <div class="radio">
                <th width = "25%">
                  <div class = "tableHeaderCol">
                    <span style = "text-align: left;">
                      Voor mij is het vanzelfsprekend dat men zich aan de coronamaatregelen behoort te houden.
                    </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#expected_compliance_0').prop('checked', true)">
                  <div class = "tableCell">
                      <label class="container">
                      <input type="radio" id="expected_compliance_0" name="expected_compliance" value=1 /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#expected_compliance_1').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="expected_compliance_1" name="expected_compliance" value=2 /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#expected_compliance_2').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="expected_compliance_2" name="expected_compliance" value=3 />  
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#expected_compliance_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="expected_compliance_3" name="expected_compliance" value=4 />  
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#expected_compliance_4').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="expected_compliance_4" name="expected_compliance" value=5 /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
            
              </div>
            </form>
            
          </tr>
          <div class="radio">
            <tr class="radio">
              <form id = "tableRow2">
                <th>
                  <div class = "tableHeaderCol">
                    <span>
                      Als er strengere coronamaatregelen worden ingevoerd behoren mensen zich hieraan te houden.
                    </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#future_compliance_0').prop('checked', true)">
                  <div class = "tableCell">
                  <label class="container">
                    <input type="radio" id="future_compliance_0" name="future_compliance" value=1 />
                    <span class="checkmark"></span>
                  </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#future_compliance_1').prop('checked', true)">
                  <div class = "tableCell">
                  <label class="container">
                    <input type="radio" id="future_compliance_1" name="future_compliance" value=2 />
                    <span class="checkmark"></span>
                  </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#future_compliance_2').prop('checked', true)">
                  <div class = "tableCell">
                  <label class="container">
                    <input type="radio" id="future_compliance_2" name="future_compliance" value=3 />
                    <span class="checkmark"></span>
                  </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#future_compliance_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="future_compliance_3" name="future_compliance" value=4 />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#future_compliance_4').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="future_compliance_4" name="future_compliance" value=5 />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
              </form>
            </tr>
          </div>
          <div class="radio">
            <tr class="radio">
              <form id = "tableRow1">
                <th>
                  <div class = "tableHeaderCol">
                    <span>
                      Ik neem het anderen kwalijk wanneer zij zich niet aan de coronamaatregelen houden.
                    </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#accountibility_0').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="accountibility_0" name="accountibility" value=1 class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#accountibility_1').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="accountibility_1" name="accountibility" value=2 class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#accountibility_2').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="accountibility_2" name="accountibility" value=3 class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#accountibility_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="accountibility_3" name="accountibility" value=4 class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#accountibility_4').prop('checked', true)">
                  <div class = "tableCell">    
                    <label class="container">      
                      <input type="radio" id="accountibility_4" name="accountibility" value=5 class = "radio"/> 
                      <span class="checkmark"></span>
                    </label>       
                  </div>
                </td> 
              </form>
            </tr>
          </div>
        </tbody>
          
      </table>
    </div>


    <div class="input-group" display="none" id="civil_obligations" method="get">
      <span class="slideText" style="">Bent u het eens of oneens met de volgende uitspraken?</span><br><br><br>
      <table class = 'questionTable'>
        <thead>
          <tr>
            <td width = "25%">   </td>
            <th width = "15%" class = "tableHeaderValues"> Helemaal oneens </th>
            <th width = "15%" class = "tableHeaderValues"> Oneens </th>
            <th width = "15%" class = "tableHeaderValues"> Een beetje eens </th>
            <th width = "15%" class = "tableHeaderValues"> Eens </th>
            <th width = "15%" class = "tableHeaderValues"> Helemaal eens </th>
          </tr>
        </thead>
        <tbody>
          <div class="radio">
            <tr class = "radio">
              <form id = "tableRow1">
                <th width = "25%">
                  <div class = "tableHeaderCol">
                    <span style = "text-align: left;">
                      Ik voel me verantwoordelijk om andere mensen niet met het coronavirus te besmetten.
                    </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#self_responsibility_0').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="self_responsibility_0" name="self_responsibility" value="1" /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#self_responsibility_1').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="self_responsibility_1" name="self_responsibility" value="2" /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#self_responsibility_2').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="self_responsibility_2" name="self_responsibility" value="3" /> 
                      <span class="checkmark"></span>
                    </label> 
                  </div>
                </td> 
                <td width = "15%" onclick="$('#self_responsibility_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="self_responsibility_3" name="self_responsibility" value="4" />  
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#self_responsibility_4').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="self_responsibility_4" name="self_responsibility" value="5" /> 
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
              </form>
            </tr>
          </div>
          <div class="radio">
            <tr class = "radio">
              <form id = "tableRow2">
                <th>
                  <div class = "tableHeaderCol">
                    <span>
                      Ik vind dat het mijn burgerplicht is om me aan de coronamaatregelen te houden.                  </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#civil_duty_0').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="civil_duty_0" name="civil_duty" value="1" />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#civil_duty_1').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="civil_duty_1" name="civil_duty" value="2" />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#civil_duty_2').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="civil_duty_2" name="civil_duty" value="3" />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#civil_duty_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="civil_duty_3" name="civil_duty" value="4" />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#civil_duty_4').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="civil_duty_4" name="civil_duty" value="5" />
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
              </form>
            </tr>
          </div>
          <div class="radio">
            <tr class = "radio">
              <form id = "tableRow1">
                <th>
                  <div class = "tableHeaderCol">
                    <span>
                      Alleen als we allemaal samenwerken krijgen we het coronavirus onder controle.                  </span>
                  </div>
                </th>
                <td width = "15%" onclick="$('#cooperation_effectiveness_0').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="cooperation_effectiveness_0" name="cooperation_effectiveness" value="1" class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#cooperation_effectiveness_1').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="cooperation_effectiveness_1" name="cooperation_effectiveness" value="2" class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#cooperation_effectiveness_2').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="cooperation_effectiveness_2" name="cooperation_effectiveness" value="3" class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#cooperation_effectiveness_3').prop('checked', true)">
                  <div class = "tableCell">
                    <label class="container">
                      <input type="radio" id="cooperation_effectiveness_3" name="cooperation_effectiveness" value="4" class = "radio"/>
                      <span class="checkmark"></span>
                    </label>
                  </div>
                </td> 
                <td width = "15%" onclick="$('#cooperation_effectiveness_4').prop('checked', true)">
                  <div class = "tableCell">  
                    <label class="container">        
                      <input type="radio" id="cooperation_effectiveness_4" name="cooperation_effectiveness" value="5" class = "radio"/> 
                      <span class="checkmark"></span>
                    </label>       
                  </div>
                </td> 
              </form>
            </tr>
          </div>
        </tbody>
          
      </table>
    </div>

    <div class="input-group radio_slide" display="none" id="gravity_situation" method="get">
      <form id="gravity_situation_form" display="none">
        <span class="slideText" style="">Hoe erg denkt u dat de huidige coronasituatie in Nederland is?</span><br><br>
        <div class="radio" onclick="$('#gravity_situation_radio_0').prop('checked', true)"><label class="container"><input type="radio" id="gravity_situation_radio_0" name="gravity_situation_radio" value=1><span class="checkmark"></span></label><span class="questionText">  Helemaal niet erg</span></div>
        <div class="radio" onclick="$('#gravity_situation_radio_1').prop('checked', true)"><label class="container"><input type="radio" id="gravity_situation_radio_1" name="gravity_situation_radio" value=2><span class="checkmark"></span></label><span class="questionText">  Niet erg</span></div>
        <div class="radio" onclick="$('#gravity_situation_radio_2').prop('checked', true)"><label class="container"><input type="radio" id="gravity_situation_radio_2" name="gravity_situation_radio" value=3><span class="checkmark"></span></label><span class="questionText">  Een beetje erg</span></div>
        <div class="radio" onclick="$('#gravity_situation_radio_3').prop('checked', true)"><label class="container"><input type="radio" id="gravity_situation_radio_3" name="gravity_situation_radio" value=4><span class="checkmark"></span></label><span class="questionText">  Erg</span></div>
        <div class="radio" onclick="$('#gravity_situation_radio_4').prop('checked', true)"><label class="container"><input type="radio" id="gravity_situation_radio_4" name="gravity_situation_radio" value=5><span class="checkmark"></span></label><span class="questionText">  Heel erg</span></div>
      </form>
    </div>

    <div class="input-group radio_slide" display="none" id="personal_impact_infection" method="get">
      <form id="personal_impact_infection_form" display="none">
        <span class="slideText" style="">Hoe gevaarlijk lijkt het u als u door het coronavirus besmet zult raken?</span><br><br>
        <div class="radio" onclick="$('#personal_impact_infection_radio_0').prop('checked', true)"><label class="container"><input type="radio" id="personal_impact_infection_radio_0" name="personal_impact_infection_radio" value=1><span class="checkmark"></span></label><span class="questionText">  Helemaal niet gevaarlijk</span></div>
        <div class="radio" onclick="$('#personal_impact_infection_radio_1').prop('checked', true)"><label class="container"><input type="radio" id="personal_impact_infection_radio_1" name="personal_impact_infection_radio" value=2><span class="checkmark"></span></label><span class="questionText">  Niet gevaarlijk</span></div>
        <div class="radio" onclick="$('#personal_impact_infection_radio_2').prop('checked', true)"><label class="container"><input type="radio" id="personal_impact_infection_radio_2" name="personal_impact_infection_radio" value=3><span class="checkmark"></span></label><span class="questionText">  Een beetje gevaarlijk</span></div>
        <div class="radio" onclick="$('#personal_impact_infection_radio_3').prop('checked', true)"><label class="container"><input type="radio" id="personal_impact_infection_radio_3" name="personal_impact_infection_radio" value=4><span class="checkmark"></span></label><span class="questionText">  Gevaarlijk</span></div>
        <div class="radio" onclick="$('#personal_impact_infection_radio_4').prop('checked', true)"><label class="container"><input type="radio" id="personal_impact_infection_radio_4" name="personal_impact_infection_radio" value=5><span class="checkmark"></span></label><span class="questionText">  Heel gevaarlijk</span></div>
      </form>
    </div>
    
    <div class="input-group radio_slide" display="none" id="slide13">
      
        <span class="slideText" style="">Hoe strikt houden deze personen zich <b>op dit moment</b> aan de coronamaatregelen van de regering?</span><br><br>
        
    </div>
    <div class="input-group radio_slide" display="none" id="slide14">
      
        <span class="slideText" style="">Hoe strikt hebben deze personen zich <b>de eerste twee maanden (april, mei)</b> aan de coronamaatregelen gehouden?</span><br><br>
        
    </div>

    <div class="input-group radio_slide" display="none" id="feedback" method="get">
      <form id="feedback_form" display="none">
        <span class="slideText" style="">Dit is het einde van de vragenlijst. Heeft u nog opmerkingen over de vragenlijst? Als u per ongeluk iets verkeerd heeft ingevuld, kunt u dat hier ook melden.</span><br><br>
        <textarea rows = "10" cols = "60" name = "feedback_field"></textarea>
      </form>
    </div>


    <div class="input-group" id="name_input" method="get" onsubmit="addAlter()">
      <input type="text" id="alterName" class="form-control" placeholder="Naam" size="10">
      <button type="submit" id="alterSubmit" class="btn btn-default" position="inline" value="Enter" onclick="addAlter()">Voeg toe</button>
    </div>


    
    <div class="popop_box" id="nonresponse_box">
      <div class="popup_box" id="popup">
            <p class="popup_text">U hebt de vraag nog niet volledig beantwoord! Het zou fijn zijn voor het onderzoek als u de vraag volledig beantwoordt. Als u wel naar de volgende vraag wil gaan, dan kunt u weer op “Ga door” klikken.</p>
            <button class="btn btn-default" onclick="closePopup()">Sluiten</button>
      </div>
    </div>

    <div class="popop_box" id="onlyone_box">
      <div class="popup_box" id="onlyOnePopup">
            <p class="popup_text">Geef een naam op.</p>
            <button class="btn btn-default" onclick="closeOnlyOnePopup()">Sluiten</button>
      </div>
    </div>

    <div class="popop_box" id="fewAlters_box">
      <div class="popup_box" id="alterPopup">
            <p class="popup_text">U heeft nog geen 8 namen genoemd. Wij zouden het erg waarderen wanneer u 8 namen noemt. Als u moeite heeft om namen te noemen, dan kunt u misschien uw contactenboek raadplegen van uw telefoon, of uw email, of via Facebook of een soortgelijke website. Als u echt geen namen meer kan verzinnen, dan kunt u verder gaan met de vragenlijst.</p>
            <button class="btn btn-default" onclick="closeAlterPopup()">Sluiten</button>
      </div>
    </div>
    
    <div class="popop_box" id="reminderAlters_box">
      <div class="popup_box" id="reminderPopup">
            <p class="popup_text">Als u moeite heeft om namen te noemen, dan kunt u misschien uw contactenboek raadplegen van uw telefoon, of uw email, of via Facebook of een soortgelijke website.</p>
            <button class="btn btn-default" onclick="closeReminderPopup()">Sluiten</button>
      </div>
    </div>

    <div id="NextDiv">
      <input type="button" 
        class="btn btn-default" 
        value="Ga door"
        id="Next"
        onclick="showNext(); pauseShowNext();" />
    </div>

    <div id="JaDiv">
      <input type="button" 
        class="btn btn-default" 
        value="Ja, ik ben akkoord met deelname"
        id="Ja"
        onclick="showNext(); pauseShowNext();" />
    </div>
    <div id="NeeDiv">
      <input type="button" 
        class="btn btn-default" 
        value="Nee, ik ben niet akkoord met deelname"
        id="Nee"
        onclick="currSlide = 100; showNext(); pauseShowNext();" />
    </div>


    
    <div id="submitForm">
      <form method="POST" action="<?php echo $_POST['returnpage']; ?>">
        <input type="hidden" name="nomem" value="<?php echo $_POST['nomem']; ?>">
        <input type="hidden" name="sh" value="<?php echo $_POST['sh']; ?>">
        <input type="hidden" name="lsi" value="<?php echo $_POST['lsi']; ?>">
        <input type="hidden" name="pli" value="<?php echo $_POST['pli']; ?>">
        <input type="hidden" name="spi" value="<?php echo $_POST['spi']; ?>">
        <input type="hidden" name="aqi" value="<?php echo $_POST['aqi']; ?>">
        <input type="hidden" name="cqi" value="<?php echo $_POST['cqi']; ?>">
        <input type="hidden" name="<?php echo $_POST['varname1']; ?>" value=""> <!-- Value leeg laten. --> 
        <input type="hidden" name="<?php echo $_POST['statusvarname1']; ?>" value="<?php echo $_POST['statusvarvalue1']; ?>">

        <input type="submit" name="<?php echo $_POST['nextvarname']; ?>" value="LISS" class="btn btn-default" /><!-- Value kan ook Volgende zijn, net wat past in jouw vragenlijst. -->
      </form>
    </div>
    
    <script type="text/javascript">
        $("#Next").css("left", center + 50 + textWidth / 2);
        console.log()
        $("#submitButton").css("left",window.innerWidth * .8);
    </script>
  </body>
</html>
