//--------------------------------
// Declaration of slides and boxes
//--------------------------------

// Slide 0

// Catch Internet Explorer users; incompatible browser
if (isIE() || isMobile()) {
  var slide0 = d3.select("svg").append("g")
    .attr("id", "slide0");
  slide0.append("rect")
    .style("fill", "white")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", bodyWidth)
    .attr("height", bodyHeight);
  slide0.append("text")
    .attr("class", "lead")
    .text("Your browser is not supported.")
    .attr("x", center - textWidth / 2)
    .attr("y", title_offset_top);
  slide0.append("text")
    .attr("class", "slideText")
    .attr("x", center - textWidth / 2)
    .attr("y", text_offset_top + title_offset_top + lineHeight)
    .text("Please us a different browser for this survey. ")
    .call(wrap, textWidth);
  document.getElementById("NextDiv").style.display="none";
} else {
  var slide_0 = d3.select("svg").append("g")
  .attr("id", "slide0");
slide_0.append("rect")
  .style("fill", "white")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_0.append("text")
  .attr("class", "lead")
  .text("")
  .attr("x", center - 170)
  .attr("y", title_offset_top);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight)
  .html("Welkom bij de vragenlijst over sociale contacten in de coronacrisis. Hartelijk dank voor uw deelname!")
  .call(wrap, textWidth);

slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 4)
  .style("font-weight", "bold")
  .text("Door wie wordt het onderzoek uitgevoerd?")
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 5)
  .text("Het onderzoek wordt uitgevoerd in opdracht van de Universiteit Utrecht. Het onderzoek is goedgekeurd door de Ethische Toetsingscommissie van de Faculteit Sociale Wetenschappen.")
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 8)
  .style("font-weight", "bold")
  .text("Hoe wordt het onderzoek uitgevoerd?")
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 9)
  .text("U wordt gevraagd om een vragenlijst in te vullen over uw sociale contacten in de coronacrisis. Dit duurt ongeveer 10 minuten. Sommige vragen kunnen gevoelig zijn omdat onderwerpen aan de orde komen waarover discussie bestaat. Daarom mag u elke vraag onbeantwoord laten als u die liever niet invult. Ook heeft u het recht zonder opgave van reden te stoppen met het onderzoek.")          
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 14)
  .style("font-weight", "bold")
  .text("Hoe gaan we met de gegevens om?")
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 15)
  .text("Om uw privacy te garanderen, werken wij volgens een wettelijk protocol. Tijdens en na het onderzoek worden uw persoonlijke gegevens niet gedeeld met de onderzoekers. Uw antwoorden zijn op geen enkele manier tot uw persoon te herleiden. Het onderzoek is dus volledig anoniem. ")          
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 19)
  .style("font-weight", "bold")
  .text("Nadere inlichtingen")
  .call(wrap, textWidth);
slide_0.append("text")
  .attr("class", "slideText")
  .attr("x", center - textWidth / 2)
  .attr("y", text_offset_top + lineHeight * 20)
  .text("Voor vragen of opmerkingen over deze vragenlijst kun je contact opnemen met dr. Tobias Stark, de projectleider: t.h.stark@uu.nl. Voor onafhankelijk advies over meedoen aan dit onderzoek kunt u terecht bij dr. Fenella Fleischmann (e-mail: f.fleischmann@uu.nl). Zij kent de achtergrond van het onderzoek, maar heeft niets te maken met het onderzoek zelf. Voor eventuele klachten over dit onderzoek kunt u terecht bij de klachtencommissie van de universiteit: klachtenfunctionaris-fetcsocwet@uu.nl.")          
  .call(wrap, textWidth);

}

// Slide 1
var slide1 = d3.select("svg").append("g")
  .attr("id", "slide1");
slide1.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide1.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight)
  .style("font-weight", "bold")
  .text("Gaat u akkoord met het volgende voor deelname aan het onderzoek?")
  .call(wrap, textWidth);
slide1.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide1 .slideText tspan').length + $('#slide1 .slideText').length))
  .text("Ik ben geïnformeerd over het onderzoek. Ik heb de schriftelijke informatie over het onderzoek op de voorgaande pagina gelezen en begrepen. Ik weet wie ik kan benaderen om vragen te stellen over het onderzoek. Ik heb de gelegenheid gekregen om over mijn deelname aan het onderzoek na te denken en mijn deelname is geheel vrijwillig. Ik stem in met het gebruik van mijn antwoorden voor wetenschappelijk onderzoek.")
  .call(wrap, textWidth);
slide1.style("display", "none");

// Slide 2

var slide2 = d3.select("svg").append("g")
  .attr("id", "slide2");
slide2.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide2.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight)
  .text("U kunt niet terug naar uw eerdere antwoorden, dus controleer uw antwoorden goed voordat u naar de volgende vraag gaat. Als u een vraag per ongeluk toch niet goed heeft ingevuld, dan kunt u dit aan het einde van de vragenlijst melden.")
  .call(wrap, textWidth);

slide2.style("display", "none");

// Slide 3       

var slide3 = d3.select("svg").append("g")
  .attr("id", "slide3");
slide3.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide3.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("De volgende vragen gaan over uw sociale netwerk. Hiermee bedoelen we mensen met wie u niet samenwoont, maar met wie u praat over dingen die voor u belangrijk zijn. ") 
  .call(wrap, textWidth);
slide3.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide3 .slideText tspan').length + $('#slide3 .slideText').length-1))
  .text("Noem alstublieft 8 voornamen van mensen van wie u vindt dat ze tot uw sociale netwerk behoren. ")
  .call(wrap, textWidth);
slide3.append("text")
  .attr("class", "slideText")
  .attr("id", "one_at_a_time")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide3 .slideText tspan').length + $('#slide3 .slideText').length-1))
  .text("Als u wilt, mag u ook bijnamen of voorletters geven, als u maar onthoudt over wie het gaat.")
  .call(wrap, textWidth);
var textheight = $('#slide3 .slideText tspan').length + $('#slide3 .slideText').length;
slide3.append("text")
  .attr("class", "slideText")
  .attr("id", "first_friend_text")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * textheight)
  .text("Als u veel moeite heeft om de lijst met 8 namen vol te maken, dan kunt u er voor kiezen om de contacten-lijst van uw (mobiele) telefoon, email, of Facebook te bekijken.")
  .call(wrap, textWidth)
  .attr("display", "none");
slide3.append("text")
  .attr("class", "slideText")
  .attr("id", "second_friend_text")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * textheight)
  .style("stroke", "none")
  .style("fill", "red")
  .text("Is there another person with whom you discuss important matters? Please enter his or her name or initials.")
  .call(wrap, textWidth)
  .attr("display", "none");
slide3.append("text")
  .attr("class", "slideText")
  .attr("id", "final_friend_text")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * textheight)
  .style("stroke", "none")
  .style("fill", "red")
  .text("Bedankt voor het invullen van de namen. Klik op \"Ga door\".")
  .call(wrap, textWidth)
  .attr("display", "none");
slide3.style("display", "none");

// Slide 4

var slide4 = d3.select("svg").append("g")
.attr("id", "slide4");
slide4.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide4.append("text")
.attr("class", "slideText numfri1")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("Wat is uw relatie tot deze personen?")
.call(wrap, textWidth);
slide4.append("text")
.attr("class", "slideText numfri2")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top + lineHeight * ($('#slide4 .slideText tspan').length + $('#slide4 .slideText').length-1))
.style("font-style", "italic")
.text("Sleep de bolletjes met uw muis naar de verschillende antwoordmogelijkheden onderaan het scherm. De bolletjes zullen van kleur veranderen wanneer deze in een vakje terecht zijn gekomen.")
.call(wrap, textWidth);
slide4.style("display", "none");

// Slide 5

var slide_5 = d3.select("svg").append("g")
.attr("id", "slide5");
slide_5.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_5.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("Wie van deze personen zijn mannen?") 
.call(wrap, textWidth);
slide_5.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top + lineHeight * ($('#slide5 .slideText tspan').length + $('#slide5 .slideText').length-1))
.style("font-style", "italic")
.text("Selecteer deze personen door met de muis op het bolletje te klikken.")
.call(wrap, textWidth);
slide_5.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top + lineHeight * ($('#slide5 .slideText tspan').length + $('#slide5 .slideText').length-1))
.style("font-style", "italic")
.text("Als dit op niemand van toepassing is, klik dan op ga door.")
.call(wrap, textWidth);
slide_5.style("display", "none");


// Slide 6
var slide_6 = d3.select("svg").append("g")
.attr("id", "slide6");
slide_6.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_6.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("Zijn deze mensen jonger dan u, ongeveer even oud of ouder dan u?") 
.call(wrap, textWidth);
slide_6.append("text")
.attr("class", "slideText numfri2")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top + lineHeight * ($('#slide6 .slideText tspan').length + $('#slide6 .slideText').length-1))
.style("font-style", "italic")
.text("Sleep de bolletjes met uw muis naar de verschillende antwoordmogelijkheden onderaan het scherm. De bolletjes zullen van kleur veranderen wanneer deze in een vakje terecht zijn gekomen.")
.call(wrap, textWidth);
slide_6.style("display", "none");

// Slide 7
var slide_7 = d3.select("svg").append("g")
  .attr("id", "slide7");
slide_7.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_7.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Wat is de hoogste opleiding die deze personen hebben afgerond?") 
  .call(wrap, textWidth);
slide_7.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide7 .slideText tspan').length + $('#slide7 .slideText').length-1))
  .text("Het is geen probleem als u het niet precies weet - geef alstublieft uw beste schatting.")
  .call(wrap, textWidth);
slide_7.style("display", "none");

// Slide 8
var slide_8 = d3.select("svg").append("g")
  .attr("id", "slide8");
slide_8.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_8.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Welke van deze personen werkt in de zorg?") 
  .call(wrap, textWidth);
slide_8.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide8 .slideText tspan').length + $('#slide8 .slideText').length-1))
  .style("font-style", "italic")
  .text("Selecteer deze personen door met de muis op het bolletje te klikken.")
  .call(wrap, textWidth);
slide_8.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide8 .slideText tspan').length + $('#slide8 .slideText').length-1))
  .style("font-style", "italic")
  .text("Als dit op niemand van toepassing is, klik dan op ga door.")
  .call(wrap, textWidth);
slide_8.style("display", "none");


// Slide 9

var slide_9 = d3.select("svg").append("g")
  .attr("id", "slide9");
slide_9.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_9.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Hoe vaak heeft u contact met deze personen? ") 
  .call(wrap, textWidth);
slide_9.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide9 .slideText tspan').length + $('#slide9 .slideText').length-1))
  .text("Met contact bedoelen we alle vormen van contact, zoals met elkaar afspreken, bellen, appen, e-mail en sociale media.")
  .call(wrap, textWidth);
slide_9.style("display", "none");

// Slide 10

var slide_10 = d3.select("svg").append("g")
  .attr("id", "slide10");
slide_10.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_10.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Hoe hecht is uw band met deze personen?") 
  .call(wrap, textWidth);
slide_10.style("display", "none");

// Slide 11

var slide_11 = d3.select("svg").append("g")
  .attr("id", "slide11");
slide_11.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_11.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Van welke personen vertrouwt u wat zij u over het coronavirus vertellen?") 
  .call(wrap, textWidth);
slide_11.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide11 .slideText tspan').length + $('#slide11 .slideText').length-1))
  .style("font-style", "italic")
  .text("Selecteer deze personen door met de muis op het bolletje te klikken.")
  .call(wrap, textWidth);
slide_11.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide11 .slideText tspan').length + $('#slide11 .slideText').length-1))
  .style("font-style", "italic")
  .text("Als dit op niemand van toepassing is, klik dan op ga door.")
  .call(wrap, textWidth);
slide_11.style("display", "none");

// // Slide 12

var slide_12 = d3.select("svg").append("g")
  .attr("id", "slide12")
slide_12.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_12.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Welke van deze personen hebben regelmatig contact met elkaar?")
  .call(wrap, textWidth);
// slide_12.append("text")
//   .attr("class", "slideText")
//   .attr("id", "contactMet1")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top + lineHeight * ($('#slide12 .slideText tspan').length + $('#slide12 .slideText').length-1))
//   .text("Als het gaat om ")
//   .call(wrap, textWidth);
slide_12.append("text")
  .attr("class", "slideText")
  .attr("id", "contactMet2")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide12 .slideText tspan').length + $('#slide12 .slideText').length-1))
  .text("Met wie heeft   contact? Met contact bedoelen we alle vormen van contact, zoals persoonlijk contact, contact via (mobiele) telefoon, post, email, sms, en andere manieren van online en offline communicatie.")
  .call(wrap, textWidth);
slide_12.append("text")
  .attr("class", "slideText")
  .attr("id", "contactMet3")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide12 .slideText tspan').length + $('#slide12 .slideText').length-1))
  .style("font-style", "italic")
  .text("Selecteer de personen die contact met elkaar hebben door met de muis op het bolletje te klikken. Er zal een lijn ontstaan die aangeeft dat de personen contact met elkaar hebben. Druk nog een keer op het bolletje om de lijn weer te laten verdwijnen, als de personen geen contact met elkaar hebben.")
  .call(wrap, textWidth);
slide_12.style("display", "none");

// slide 13
// var slide_13 = d3.select("svg").append("g")
//   .attr("id", "slide13");
// slide_13.append("rect") 
//   .style("fill", "white")
//   .attr("class", "slide")
//   .attr("x", 0)
//   .attr("y", 0)
//   .attr("width", bodyWidth)
//   .attr("height", bodyHeight);
// slide_13.append("text")
//   .attr("class", "slideText")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top)
//   .text("Hoe strikt houden de mensen in uw netwerk zich op dit moment aan de coronamaatregelen van de regering?") 
//   .call(wrap, textWidth);
// slide_13.append("text")
//   .attr("class", "slideText")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top + lineHeight * ($('#slide13 .slideText tspan').length + $('#slide13 .slideText').length-1))
//   .text("Sleep de bolletjes met uw muis naar de verschillende antwoordmogelijkheden onderaan het scherm. De bolletjes zullen van kleur veranderen wanneer deze in een vakje terecht zijn gekomen. ")
//   .call(wrap, textWidth);
// slide_13.style("display", "none");

// slide 14
// var slide_14 = d3.select("svg").append("g")
// .attr("id", "slide14");
// slide_14.append("rect") 
// .style("fill", "white")
// .attr("class", "slide")
// .attr("x", 0)
// .attr("y", 0)
// .attr("width", bodyWidth)
// .attr("height", bodyHeight);
// slide_14.append("text")
// .attr("class", "slideText")
// .attr("x", center - (textWidth / 2))
// .attr("y", text_offset_top)
// .text("Hoe strikt hebben deze personen zich de eerste twee maanden (april, mei) aan de coronamaatregelen gehouden?")
// .call(wrap, textWidth);
// slide_14.style("display", "none");

// slide 15
var slide_15 = d3.select("svg").append("g")
.attr("id", "slide15");
slide_15.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_15.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("In hoeverre vinden deze personen dat men zich aan de coronamaatregelen behoort te houden?") 
.call(wrap, textWidth);
slide_15.style("display", "none");

// slide 16
var slide_16 = d3.select("svg").append("g")
.attr("id", "slide16");
slide_16.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_16.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("In hoeverre vinden deze personen de huidige coronamaatregelen overdreven?") 
.call(wrap, textWidth);
slide_16.style("display", "none");

// slide 17
var slide_17 = d3.select("svg").append("g")
.attr("id", "slide17");
slide_17.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_17.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("In hoeverre vinden deze personen dat het hun burgerplicht is om zich aan de coronamaatregelen te houden?") 
.call(wrap, textWidth);
slide_17.style("display", "none");

// slide 18
var slide_18 = d3.select("svg").append("g")
.attr("id", "slide18");
slide_18.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_18.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("Stel dat u uw verjaardag viert en deze acht personen zijn uw gasten. Hoe waarschijnlijk is het dat u iedereen er aan herinnert om afstand te houden wanneer ze te dicht bij elkaar zijn?") 
.call(wrap, textWidth);
slide_18.style("display", "none");

// slide 19
var slide_19 = d3.select("svg").append("g")
.attr("id", "slide19");
slide_19.append("rect") 
.style("fill", "white")
.attr("class", "slide")
.attr("x", 0)
.attr("y", 0)
.attr("width", bodyWidth)
.attr("height", bodyHeight);
slide_19.append("text")
.attr("class", "slideText")
.attr("x", center - (textWidth / 2))
.attr("y", text_offset_top)
.text("Stel dat u uw verjaardag viert en deze acht personen zijn uw gasten. Een van de gasten vertelt dat hij/zij zich niet lekker voelt en milde klachten heeft. Hoe waarschijnlijk is het dat u hem/haar vraagt de verjaardag te verlaten?") 
.call(wrap, textWidth);
slide_19.style("display", "none");

//slide19_1
var slide_19_1 = d3.select("svg").append("g")
  .attr("id", "slide19_1");
slide_19_1.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_19_1.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Bij de volgende drie vragen verschijnt er naast de personen uit uw sociale netwerk een nieuw bolletje: ‘Uzelf’. Met dit bolletje kunt u aangeven hoe u zelf denkt over de vragen die aan u gesteld worden. ") 
  .call(wrap, textWidth);
slide_19_1.style("display", "none");
// slide 20
var slide_20 = d3.select("svg").append("g")
  .attr("id", "slide20");
slide_20.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_20.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Welke personen behoren tot een risicogroep voor het coronavirus? En uzelf?") 
  .call(wrap, textWidth);
slide_20.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide20 .slideText tspan').length + $('#slide20 .slideText').length-1))
  .text("Het is geen probleem als u het niet precies weet - geef alstublieft uw beste schatting. ")
  .call(wrap, textWidth);
slide_20.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide20 .slideText tspan').length + $('#slide20 .slideText').length-1))
  .style("font-style", "italic")
  .text("Selecteer deze personen door met de muis op het bolletje te klikken.")
  .call(wrap, textWidth);
slide_20.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide20 .slideText tspan').length + $('#slide20 .slideText').length-1))
  .style("font-style", "italic")
  .text("Als dit op niemand van toepassing is, klik dan op ga door.")
  .call(wrap, textWidth);
  
slide_20.style("display", "none");

// slide 21
var slide_21 = d3.select("svg").append("g")
  .attr("id", "slide21");
slide_21.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_21.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Van welke van deze personen denkt u dat zij besmet zijn geweest met het coronavirus? En uzelf?") 
  .call(wrap, textWidth);
slide_21.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide21 .slideText tspan').length + $('#slide21 .slideText').length-1))
  .text("Het is geen probleem als u het niet precies weet - geef alstublieft uw beste schatting. ")
  .call(wrap, textWidth);
slide_21.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide21 .slideText tspan').length + $('#slide21 .slideText').length-1))
  .style("font-style", "italic")
  .text("Selecteer deze personen door met de muis op het bolletje te klikken.")
  .call(wrap, textWidth);
slide_21.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide21 .slideText tspan').length + $('#slide21 .slideText').length-1))
  .style("font-style", "italic")
  .text("Als dit op niemand van toepassing is, klik dan op ga door.")
  .call(wrap, textWidth);
slide_21.style("display", "none");

// slide 22
var slide_22 = d3.select("svg").append("g")
  .attr("id", "slide22");
slide_22.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_22.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Er is discussie over de vraag of we wel de hele waarheid te horen krijgen over het coronavirus. Sommigen denken dat de mainstream media en politieke elite een verborgen agenda hebben en de waarheid over het coronavirus achterhouden.  ") 
  .call(wrap, textWidth);
slide_22.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top + lineHeight * ($('#slide22 .slideText tspan').length + $('#slide22 .slideText').length-1))
  .text("In hoeverre zijn deze personen het hiermee eens? En uzelf?  ")
  .call(wrap, textWidth);
slide_22.style("display", "none");

// // slide 23
// var slide_23 = d3.select("svg").append("g")
//   .attr("id", "slide23");
// slide_23.append("rect") 
//   .style("fill", "white")
//   .attr("class", "slide")
//   .attr("x", 0)
//   .attr("y", 0)
//   .attr("width", bodyWidth)
//   .attr("height", bodyHeight);
// slide_23.append("text")
//   .attr("class", "slideText")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top)
//   .text("Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine zou moeten gaan. U heeft echter geen klachten. Hoe waarschijnlijk is het dat u in quarantaine zult gaan? ") 
//   .call(wrap, textWidth);
// slide_23.style("display", "none");

// // slide 24
// var slide_24 = d3.select("svg").append("g")
//   .attr("id", "slide24");
// slide_24.append("rect") 
//   .style("fill", "white")
//   .attr("class", "slide")
//   .attr("x", 0)
//   .attr("y", 0)
//   .attr("width", bodyWidth)
//   .attr("height", bodyHeight);
// slide_24.append("text")
//   .attr("class", "slideText")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top)
//   .text("Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine zou moeten gaan. U heeft echter geen klachten. Goede vrienden van u vinden dat u alsnog in thuisquarantaine behoort te gaan. Hoe waarschijnlijk is het dat u in quarantaine zult gaan?") 
//   .call(wrap, textWidth);
// slide_24.style("display", "none");

// // slide 25
// var slide_25 = d3.select("svg").append("g")
//   .attr("id", "slide25");
// slide_25.append("rect") 
//   .style("fill", "white")
//   .attr("class", "slide")
//   .attr("x", 0)
//   .attr("y", 0)
//   .attr("width", bodyWidth)
//   .attr("height", bodyHeight);
// slide_25.append("text")
//   .attr("class", "slideText")
//   .attr("x", center - (textWidth / 2))
//   .attr("y", text_offset_top)
//   .text("Stel u voor dat u op vakantie bent geweest naar Spanje. U weet dat u na terugkeer 10 dagen in thuisquarantaine zou moeten gaan. U heeft echter geen klachten. Goede vrienden vinden dat u dan ook niet in thuisquarantaine behoort te gaan. Hoe waarschijnlijk is het dat u in quarantaine zult gaan? ") 
//   .call(wrap, textWidth);
// slide_25.style("display", "none");
// slide 26
var slide_26 = d3.select("svg").append("g")
  .attr("id", "slide26");
slide_26.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_26.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt hierdoor of het wel verstandig is om naar de verjaardag te gaan. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan?") 
  .call(wrap, textWidth);
slide_26.style("display", "none");
// slide 27
var slide_27 = d3.select("svg").append("g")
  .attr("id", "slide27");
slide_27.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_27.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt hierdoor of het wel verstandig is om naar de verjaardag te gaan. Goede vrienden van u gaan echter wel naar de verjaardag. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan?") 
  .call(wrap, textWidth);
slide_27.style("display", "none");
// slide 28
var slide_28 = d3.select("svg").append("g")
  .attr("id", "slide28");
slide_28.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
slide_28.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Stel u voor dat u uitgenodigd bent voor een verjaardag. U weet dat het huis niet groot genoeg is om 1.5 meter afstand te houden. U twijfelt hierdoor of het wel verstandig is om naar de verjaardag te gaan. Goede vrienden van u hebben besloten om hierdoor niet naar de verjaardag te gaan. Hoe waarschijnlijk is het dat u naar de verjaardag zult gaan?") 
  .call(wrap, textWidth);
slide_28.style("display", "none");

var complete = d3.select("svg").append("g")
  .attr("id", "complete");
complete.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
complete.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("Bedankt voor het invullen van de vragenlijst! U wordt nu teruggeleid naar de website van Motivaction. Sluit dit venster niet af!") 
  .call(wrap, textWidth);
complete.style("display", "none");

var screenout = d3.select("svg").append("g")
  .attr("id", "screenout");
screenout.append("rect") 
  .style("fill", "white")
  .attr("class", "slide")
  .attr("x", 0)
  .attr("y", 0)
  .attr("width", bodyWidth)
  .attr("height", bodyHeight);
screenout.append("text")
  .attr("class", "slideText")
  .attr("x", center - (textWidth / 2))
  .attr("y", text_offset_top)
  .text("U bent niet akkoord gegaan met deelname aan de survey, u wordt nu teruggeleid naar de website van Motivaction. Sluit dit venster niet af!") 
  .call(wrap, textWidth);
screenout.style("display", "none");
