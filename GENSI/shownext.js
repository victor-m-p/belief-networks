// ---------------------------------------------------------------------------------------
// showNext(): Prepares for next slide in survey. Hides previous slide and shows currSlide,
// performing whatever operations needed for preparing slide.
// A bit like the main() function
// ---------------------------------------------------------------------------------------

function showNext() {
  console.log(answers.keys().length);
  if (currSlide == 0) {

    var d = new Date();
    startTime = d.getTime();

    answers['d'] = urlParams.get('d');
    answers['k'] = urlParams.get('k');
    

    // respondent ID tbd
    ///////////
    
    // Informed consent
    document.getElementById("Next").style.position="absolute";
    document.getElementById("Next").style.left= (center + 50 + textWidth / 2) + "px";
    document.getElementById("slide0").style.display = "none";
    document.getElementById("Next").style.display = "none";

    document.getElementById("slide1").style.display = "block";
    document.getElementById("Ja").style.display = "block";
    document.getElementById("Nee").style.display = "block";


    currSlide++;
    
  } else if (currSlide == 1) {
    document.getElementById("slide1").style.display = "none";
    document.getElementById("Ja").style.display = "none";
    document.getElementById("Nee").style.display = "none";

    answers.consent = true;
    document.getElementById("slide2").style.display = "block";
    document.getElementById("Next").style.display = "block";
    currSlide++;
    
    
  } else if (currSlide == 2) {
    document.getElementById("slide2").style.display = "none";

    // Q1: Hoe strict houdt u zich aan de Coronaregels?

    var ex = document.getElementById("self_strictness");
    ex.style.left = string_l + "px";
    ex.style.top = string_t;
    ex.style.display = "block";
    
   

    currSlide++;
    
  } else if (currSlide == 3) {
    // If user has not selected an option, alert with popup
    if ($('input[name=self_strictness_radio]:checked').length == 0 && checked == false) {
      promptNonresponse();
      checked = true;
    } else {

      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=self_strictness_radio]:checked').val();
      keys.push("q" + currQuestion);


      document.getElementById("self_strictness").style.display = "none";
      checked = false;
      currQuestion++;
      currSlide++;
      showNext();
    }
  } else if (currSlide == 4) {
    d3.selectAll(".node").attr("display", "block");
   
    //Q2: Namen sociaal netwerk
    document.getElementById("slide3").style.display = "block";
    document.getElementById("name_input").style.display = "inline-flex";
    document.getElementById("name_input").style.left = string_l + "px";

    for(i = 1;i <= 8;i++) {
      
      var d = new Date();
      var node = {name: i, 
                  id: i, 
                  timeStamp:(d - startTime) / 1000,
                  male:false, 
                  healthcare_worker:false,
                  trustworthy:false,
                  risk_group:false,
                  infected:false,
                  kids:"nee",
                  friends:"nee",
                  kinderwens:"nee",
                  kinderloos:"nee",
                  kinderhulp:"nee",
                  kinderpraat:"nee",
                  xx:(bodyWidth/8)+(bodyWidth/9*(i-1)),
                  yy:((bodyWidth/8)+(bodyWidth/9)<8)?nodeLine+(i % 3)*40:nodeLine+(i % 2)*40,
                  x:(bodyWidth/8)+(bodyWidth/9*(i-1)),
                  y:((bodyWidth/8)+(bodyWidth/9)<8)?nodeLine+(i % 3)*40:nodeLine+(i % 2)*40};
    
      var focus = {id: i,
                  x:i*(bodyWidth/8)-(bodyWidth/8)/2,
                  y:((bodyWidth/8)+(bodyWidth/9)<8)?nodeLine+(i % 3)*40:nodeLine+(i % 2)*40};
    
      n = nodes.push(node);
      f = foci.push(focus);
    }

    setTimeout(function() {
      if(currSlide == 4) {
        alterPromptReminder();
      }
    },900000);

    restart();
    d3.selectAll(".node").attr("opacity", "0.4");

    currSlide++;

  } else if (currSlide == 5) {
    if (numAlters < 8 && checked == false) {
      checked = numAlters < 1 ? false : true;
      
      alterpromptNonresponse();
    } else {

      checked = false;
      nodes.forEach(function(d) {
        
        if (d.id > numAlters) {
          d.name = undefined;
          d.male = undefined;
          d.healthcare_worker = false;
          d.infected = false;
          d.risk_group = false;
          d.trustworthy = false;
          d.kids = undefined;
          d.friends = undefined;
          d.kinderwens = undefined;
          d.kinderloos = undefined;
          d.kinderhulp = undefined;
          d.kinderpraat = undefined;
          answers["q2_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = d.name;
          var qd = new Date();
        }
      });
      resetFoci(false);
      for (i = 1; i <= numAlters; i++) {
        keys.push("q2_0" + i);
      }
      document.getElementById("slide3").style.display = "none";

      // Q3: Wat is uw relatie tot deze personen
      document.getElementById("slide4").style.display = "block";
      document.getElementById("sixBar").style.display = "block";
      document.getElementById("relationship_labels").style.display = "block";


      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
      },1000);
      document.getElementById("name_input").style.display = "none";
      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 6) {
    // If user has not selected an option, alert with popup
    if (!altersInBoxes(6, false) && !checked) {
     
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 6, false);
      
      checked = false;
      document.getElementById("slide4").style.display = "none";
      document.getElementById("sixBar").style.display = "none";
      document.getElementById("relationship_labels").style.display = "none";

      // Q4: Wie van deze personen zijn mannen.
      document.getElementById("slide5").style.display = "block";
      restart();
      clearColors();
      
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      
      currQuestion++;
      currSlide++;
    }
  
  } else if (currSlide == 7) {
    
    // Collect data before going on
    for (i = 1; i <= numAlters; i++) {
      answers["q" + currQuestion + "_0" + i] = nodes[i].male;
      keys.push("q" + currQuestion + "_0" + i);
    }

    document.getElementById("slide5").style.display = "none";

    //Q5: Zijn deze mensen joger, ongeveer even oud, of ouder dan u?
    document.getElementById("slide6").style.display = "block";
    document.getElementById("relative_age_labels").style.display = "block";
    document.getElementById("fiveBar").style.display = "block";


    clearColors();
    resetFoci(false);
    currSlide++;
    currQuestion++;
    d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
    setTimeout(function() {
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
    },1000);

  } else if (currSlide == 8) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {

      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);
      

      checked = false;
      
      document.getElementById("slide6").style.display = "none";
      document.getElementById("relative_age_labels").style.display = "none";
      document.getElementById("fiveBar").style.display = "none";

      // Q6: Wat is de hoogste opleiding die deze mensen hebben afgerond.
      document.getElementById("slide7").style.display = "block";
      document.getElementById("education_labels").style.display = "block";
      document.getElementById("threeBar").style.display = "block";

      clearColors();
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
      },1000);
      currSlide ++;
      currQuestion++;
    }
  } else if (currSlide == 9) {
    // If user has not selected an option, alert with popup
    if (!altersInBoxes(3, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 3, false);
      
      checked = false;

      document.getElementById("slide7").style.display = "none";
      document.getElementById("education_labels").style.display = "none";
      document.getElementById("threeBar").style.display = "none";

      // Q7: Welke van deze personen werke in de zorg?
      document.getElementById("slide8").style.display = "block";

      restart();

      clearColors()
      resetFoci(false)
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      

      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 10) {
    // If user has not selected an option, alert with popup
  
    for (i = 1; i<= numAlters; i++) {
      answers["q" + currQuestion + "_0" + i] = nodes[i].healthcare_worker;
      keys.push("q" + currQuestion + "_0" + i);
    } 

    checked = false;

    document.getElementById("slide8").style.display = "none";
    

    // Q8: Hoe vaak heeft u contact met deze mensen?
    document.getElementById("slide9").style.display = "block";
    document.getElementById("fiveBar").style.display = "block";
    document.getElementById("frequency_labels").style.display = "block";

    restart();

    resetFoci(false);
    clearColors();

    d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
    setTimeout(function() {
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
      d3.selectAll(".link").attr("display", "none");  
      
    },1000);

    currSlide++;
    currQuestion++;
  
  } else if (currSlide == 11) {
    // If user has not selected an option, alert with popup
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);
     
      checked = false;

      document.getElementById("slide9").style.display = "none";
      document.getElementById("fiveBar").style.display = "none";
      document.getElementById("frequency_labels").style.display = "none";

      // Q9: Hoe hecht is uw band met deze personen?

      document.getElementById("slide10").style.display = "block";
      document.getElementById("fiveBar").style.display = "block";
      document.getElementById("closeness_labels").style.display = "block";

      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        
      },1000);

      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 12) {
    // If user has not selected an option, alert with popup
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);
      

      checked = false;

      document.getElementById("slide10").style.display = "none";
      document.getElementById("fiveBar").style.display = "none";
      document.getElementById("closeness_labels").style.display = "none";

      // Q10: Van welke personen vertrouwt u wat zij u over het coronavirus vertellen?

      document.getElementById("slide11").style.display = "block";

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      clearColors();
      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 13) {
    // Collect data before going on
    for (i = 1; i<= numAlters; i++) {
      answers["q" + currQuestion + "_0" + i] = nodes[i].trustworthy;
      keys.push("q" + currQuestion + "_0" + i);
    }
    currSlide++;
    currQuestion++;
    showNext();
  } else if (currSlide == 14) {
    
    checked = false; 
    altered = false;          

    document.getElementById("slide11").style.display = "none";

    d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
    // Q11: Connecties maken

    var n = numAlters,      // number of child nodes
        r = 160      // radius

    for (var i=1; i<=numAlters; i++) {
      var theta = (i / numAlters * Math.PI * 2) - 2;
      foci[i].ox = foci[i].x;
      if(numAlters < 18) {
        foci[i].x = center + r*Math.cos(theta);
      } else {
        foci[i].x = center + ((i % 2)?1.15*r:r)*Math.cos(theta);
      }
      foci[i].oy = foci[i].y;
      if(numAlters < 18) {
        foci[i].y = 580 + r*Math.sin(theta);
      } else {
        foci[i].y = 580 + ((i % 2)?1.15*r:r)*Math.sin(theta);
      }
    }

      /*foci[i].x = center + ((numAlters<20)?r:((i % 2)*0.8)*r)*Math.cos(theta);
      foci[i].oy = foci[i].y;
      foci[i].y = 500 + ((numAlters<20)?r:((i % 2)*0.8)*r)*Math.sin(theta);*/

    restart();
    clearColors();

    document.getElementById("slide12").style.display = "block";

    currSlide++;
    setTimeout(function() {
      showNext();
    },1000);
  
  } else if (currSlide == 15) {
    // Q: Lijnen trekken
    console.log(askedAbout);
    if (askedAbout > 0) {

      connections = [];
      for (i = 1; i <= numAlters; i++) {
        if(nodes[askedAbout][i] == 1) {
          if(connections == []) {
            connections = [i];
          } else {
            connections.push(i);
          }
        }
      }
      for (i = askedAbout + 1; i <= numAlters; i++) {
        answers["q" + currQuestion + "_0" + askedAbout + "_0" + i] = connections.includes(i);     
      }

      foci[askedAbout].x = foci[askedAbout].px
      foci[askedAbout].y = foci[askedAbout].py

      links.splice(0,links.length);
      d3.selectAll(".node").attr("opacity", function(d) { return d.index <= askedAbout ? 0 : 1 });
    }

    if (askedAbout+1 == numAlters) {
      // Collect data before going on
      // nodes.forEach(function(d) {
      //   if (d.id > numAlters-1) {
      //     answers["q" + currQuestion + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;
      //   }
      // });

    
      /*for (var i=1; i<=numAlters; i++) {
        foci[i].x = foci[i].ox;
        foci[i].y = foci[i].oy;
      }*/
      
      d3.selectAll(".node").attr("display", "block");
      d3.selectAll(".node").attr("opacity", 1);
      d3.selectAll(".link").attr("display", "none");  
      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        //d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);

      resetFoci(false);
      clearColors();
      document.getElementById("slide12").style.display = "none";
      
      // Q12: Hoe strikt houden de mensen in uw netwerk zich op dit moment aan de coronamaatregelen van de regering?
      var ex = document.getElementById("slide13");
      ex.style.left = (center - (textWidth / 2) - 5) + "px";
      ex.style.top = (text_offset_top - 10) + "px";
      ex.style.display = "block";
      document.getElementById("fiveBar").style.display = "block";
      document.getElementById("compliance_labels").style.display = "block";
      
      for (i = 1; i <= numAlters; i++) {
        keys.push("q" + currQuestion + "_0" + i);
      }
      
      askedAbout = 0;
      currSlide++;
      currQuestion++;
      checked = false;
      
    } else {
      askedAbout++;
      
      currNode = nodes[askedAbout];
      $("#contactMet1").text("ALS HET GAAT OM " + currNode.name.toUpperCase());
      $("#contactMet2").text("Met wie heeft " + currNode.name.toUpperCase() + " contact? Met contact bedoelen we alle vormen van contact, zoals persoonlijk contact, contact via (mobiele) telefoon, post, email, sms, en andere manieren van online en offline communicatie.");
      d3.selectAll("#contactMet2").call(wrap, textWidth);
      $("#contactMet3").attr("y", text_offset_top + lineHeight * ($('#slide14 .slideText tspan').length + $('#slide14 .slideText').length-1))

      foci[askedAbout].px = foci[askedAbout].x
      foci[askedAbout].py = foci[askedAbout].y
      
      foci[askedAbout].x = center;
      foci[askedAbout].y = 580;
      d3.selectAll(".node").style("fill", function(d) { return d.index == askedAbout ? selfColor : nodeColor });
      restart();
    }
  } else if (currSlide == 16) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);
      
      checked = false;

      document.getElementById("slide13").style.display = "none";
      

      // Q13: Hoe strikt hebben deze personen zich de eerste twee maanden (april, mei) aan de coronamaatregelen gehouden?

      
      var ex = document.getElementById("slide14");
      ex.style.left = (center - (textWidth / 2) - 5) + "px";
      ex.style.top = (text_offset_top - 10) + "px";
      ex.style.display = "block";

      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        // d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);

      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 17) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);

      checked = false;

      document.getElementById("slide14").style.display = "none";
      document.getElementById("compliance_labels").style.display = "none";
      

      // Q14: In hoeverre vinden deze personen dat men zich aan de coronamaatregelen behoort te houden?

      document.getElementById("slide15").style.display = "block";
      document.getElementById("norms_labels").style.display = "block";
      
      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        // d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);

      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 18) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);
      
      checked = false;

      document.getElementById("slide15").style.display = "none";
      

      // Q15: In hoeverre vinden deze personen de huidige coronamaatregelen overdreven?

      document.getElementById("slide16").style.display = "block";
      
      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        // d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);

      currQuestion++;
      currSlide++;
    }
    
  } else if (currSlide == 19) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);

      checked = false;

      document.getElementById("slide16").style.display = "none";
      

      // Q16: In hoeverre vinden deze personen dat het hun burgerplicht is om zich aan de coronamaatregelen te houden?

      document.getElementById("slide17").style.display = "block";
      
      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
      },1000);

      currQuestion++;
      currSlide++;
    }

  } else if (currSlide == 20) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);

      checked = false;

      document.getElementById("slide17").style.display = "none";
      document.getElementById("norms_labels").style.display = "none";
      

      // Q4: How close is your relationship with each person?
      document.getElementById("slide18").style.display = "block";
      document.getElementById("social_sanctions_labels").style.display = "block";
    
      
      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        // d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);
      currSlide++;
      currQuestion++;
    }

  } else if (currSlide == 21) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);

      checked = false;

      document.getElementById("slide18").style.display = "none";
      
      

      // Q4: How close is your relationship with each person?
      document.getElementById("slide19").style.display = "block";
    
      
      clearColors();
      restart();

      d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        d3.selectAll(".node").attr("opacity", 1);
        d3.selectAll(".node").style("fill", function(d) { return d.index == 0 ? selfColor : nodeColor });
      },1000);
      currSlide++;
      currQuestion++;
    }

  } else if (currSlide == 22) {
    if (!altersInBoxes(5, false) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, false);

      checked = false;

      document.getElementById("slide19").style.display = "none";
      document.getElementById("social_sanctions_labels").style.display = "none";
      document.getElementById("fiveBar").style.display = "none";


      // Q4: How close is your relationship with each person?
      document.getElementById("slide19_1").style.display = "block";
      
    
      
      clearColors();
      restart();
      resetFoci(true)
      d3.selectAll(".node").attr("display", "none");
      
      currSlide += .5;
      currQuestion++;
    }

  } else if (currSlide == 22.5) {
    document.getElementById("slide19_1").style.display = "none";

    document.getElementById("slide20").style.display = "block";
    clearColors();
    d3.selectAll(".node").attr("display", "block");
    resetFoci(true)
    d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});

    currSlide += .5;
  } else if (currSlide == 23) {
    document.getElementById("slide20").style.display = "none";

    document.getElementById("slide21").style.display = "block";

    for (i = 0; i<= numAlters; i++) {
      answers["q" + currQuestion + "_0" + i] = nodes[i].risk_group;
    }
    clearColors();
    resetFoci(true);
    currSlide++;
    currQuestion++;

  } else if (currSlide == 24) {

    for (i = 0; i<= numAlters; i++) {
      answers["q" + currQuestion + "_0" + i] = nodes[i].infected;
      keys.push("q" + currQuestion + "_0" + i);
    }
    document.getElementById("slide21").style.display = "none";

    document.getElementById("slide22").style.display = "block";
    document.getElementById("fiveBar").style.display = "block";
    document.getElementById("norms_labels").style.display = "block";
    
    d3.selectAll(".node").classed("fixed", function(d) { d.fixed = false});
      setTimeout(function() {
        d3.selectAll(".node").classed("fixed", function(d) { d.fixed = true});
        d3.selectAll(".link").attr("display", "none");  
        // d3.selectAll(".node").attr("opacity", function(d) { return d.index == 0 ? .4 : 1 });
      },1000);
    
    clearColors();
    resetFoci(true);
    currSlide++;
    currQuestion++;

  } else if (currSlide == 25) {
    if (!altersInBoxes(5, true) && !checked) {
      promptNonresponse();
      checked = true;
    } else {
      // Collect data before going on
      saveAltersInBoxes(currQuestion, 5, true);

      checked = false;

      document.getElementById("slide22").style.display = "none";
      document.getElementById("norms_labels").style.display = "none";
      document.getElementById("fiveBar").style.display = "none";
      d3.selectAll(".node").attr("display", "none"); 

      answers.scenario = in_between_0;
      var in_between_slides = ["slide23_0", "slide23_1", "slide23_2"];

      var ex = document.getElementById("slide23");
      ex.style.left = string_l + "px";
      ex.style.top = string_radio;
      ex.style.display = "block";

      var ex = document.getElementById(in_between_slides[in_between_0]);
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";
      
      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 26) {
    if ($('input[name=between_subject_radio_0]:checked').length == 0 && checked == false) {
      promptNonresponse();
      checked = true;
    } else {
      
      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=between_subject_radio_0]:checked').val();
      keys.push("q" + currQuestion);

      checked = false;

      var in_between_slides_0 = ["slide23_0", "slide23_1", "slide23_2"];
      document.getElementById(in_between_slides_0[in_between_0]).style.display = "none";
      var to_uncheck = $('input[name=between_subject_radio_0]:checked');
      
      to_uncheck.prop("checked", false);
      
      var in_between_slides_1 = ["slide24_0", "slide24_1", "slide24_2"];
      var ex = document.getElementById(in_between_slides_1[in_between_0]);
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";      
      
      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 27) {
    if ($('input[name=between_subject_radio_0]:checked').length == 0 && checked == false) {
      promptNonresponse();
      checked = true;
    } else {
      answers["q" + currQuestion] = $('input[name=between_subject_radio_0]:checked').val();
      keys.push("q" + currQuestion);

      var in_between_slides_1 = ["slide24_0", "slide24_1", "slide24_2"];
      document.getElementById(in_between_slides_1[in_between_0]).style.display = "none";
      document.getElementById("slide23").style.display = "none";
      
      checked = false;

      var ex = document.getElementById("moral_obligations");
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";

      currSlide++;
      currQuestion++;
    }
  } else if (currSlide == 28) {
    if (($('input[name=expected_compliance]:checked').length == 0 && checked == false) ||
        ($('input[name=future_compliance]:checked').length == 0 && checked == false) ||
        ($('input[name=expected_compliance]:checked').length == 0 && checked == false)) {
      promptNonresponse();
      checked = true;
    } else {
      
      document.getElementById("moral_obligations").style.display = "none";
      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=expected_compliance]:checked').val();
      answers["q" + (currQuestion + 1)] = $('input[name=future_compliance]:checked').val();
      answers["q" + (currQuestion + 2)] = $('input[name=accountibility]:checked').val();
      
      keys.push("q" + currQuestion);
      keys.push("q" + (currQuestion + 1));
      keys.push("q" + (currQuestion + 2));
      checked = false;
      currSlide++;
      currQuestion += 3;

      var ex = document.getElementById("civil_obligations");
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";
      
    }

  } else if (currSlide == 29) {
    if (($('input[name=self_responsibility]:checked').length == 0 && checked == false) ||
        ($('input[name=civil_duty]:checked').length == 0 && checked == false) ||
        ($('input[name=cooperation_effectiveness]:checked').length == 0 && checked == false)) {
      promptNonresponse();
      checked = true;
    } else {
      
      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=self_responsibility]:checked').val();
      answers["q" + (currQuestion + 1)] = $('input[name=civil_duty]:checked').val();
      answers["q" + (currQuestion + 2)] = $('input[name=cooperation_effectiveness]:checked').val();

      keys.push("q" + currQuestion);
      keys.push("q" + (currQuestion + 1));
      keys.push("q" + (currQuestion + 2));

      document.getElementById("civil_obligations").style.display = "none";
      checked = false;

      currSlide++;
      currQuestion += 3;

      var ex = document.getElementById("gravity_situation");
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";
      
    }

  } else if (currSlide == 30) {
    if ($('input[name=gravity_situation_radio]:checked').length == 0 && checked == false) {
      promptNonresponse();
      checked = true;
    } else {
      
      document.getElementById("gravity_situation").style.display = "none";
      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=gravity_situation_radio]:checked').val();
      keys.push("q" + currQuestion);

      

      
      checked = false;
      currSlide++;
      currQuestion++;

      var ex = document.getElementById("personal_impact_infection");
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";
      
    }

  } else if (currSlide == 31) {
    if ($('input[name=personal_impact_infection_radio]:checked').length == 0 && checked == false) {
      promptNonresponse();
      checked = true;
    } else {
      
      document.getElementById("personal_impact_infection").style.display = "none";
      // Collect data before going on
      answers["q" + currQuestion] = $('input[name=personal_impact_infection_radio]:checked').val();
      keys.push("q" + currQuestion);
     
      
      checked = false;
      currSlide++;
      currQuestion++;

      var ex = document.getElementById("feedback");
      ex.style.left = string_l + "px";
      ex.style.top = string_t;
      ex.style.display = "block";
      
    }

  } else if (currSlide == 32) {
    document.getElementById("feedback").style.display = "none";
    document.getElementById("NextDiv").style.display = "none";

    document.getElementById("complete").style.display = "block";

    answers.feedback = $('textarea[name=feedback_field]').val();
    
    var d = new Date();
    answers.elapsed_time = (d - startTime) / 1000;

    var answer = [];
    for (var i in answers) {
      if (answers[i] == undefined) answers[i] = 9999;
      if (answers[i] == true) answers[i] = 1;
      if (answers[i] == false) answers[i] = 0;

      answer.push(answers[i]);
    }
    console.log(answer.length);
    answer = answer.join(';');
    
    // $.post("save_results.php", { a: answer });
    
    
    $.ajax({
      type : "POST",  //type of method
      url  : "save_results.php",  //your page
      data : { a: answer },// passing the values
      success: function(res){  
        console.log("success!")
      }
    });
    unhook();
    setTimeout(function() {
      //window.location.href = "https://www.stempunt.nu/s.asp?d=" + urlParams.get('d') + "&k=" + urlParams.get('k') + "&extid=01";
    },3000);
    
    
  } else if (currSlide == 100) {
    document.getElementById("slide1").style.display = "none";
    document.getElementById("Ja").style.display = "none";
    document.getElementById("Nee").style.display = "none";

    document.getElementById("screenout").style.display = "block";

    
    setTimeout(function() {
      unhook();
      //window.location.href = "https://www.stempunt.nu/s.asp?d=" + urlParams.get('d') + "&k=" + urlParams.get('k') + "&extid=02";
    },3000);


  }
  
  $('#Next').blur();
  
}