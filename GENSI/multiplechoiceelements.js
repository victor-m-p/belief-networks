// Boxes indicating frequency into which nodes are dragged (3, 4, 5 or 6 categories)
var threeBar = d3.select("svg").append("g")
  .attr("id", "threeBar")
  .style("display", "none")

threeBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "one")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y)
  .attr("width", bar3_target_width)
  .attr("height", bar_target_height);

threeBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "one_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar3_target_width)
  .attr("height", bar_label_height);

threeBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "two")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar3_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y)
  .attr("width", bar3_target_width)
  .attr("height", bar_target_height);

threeBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "two_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar3_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar3_target_width)
  .attr("height", bar_label_height); 

threeBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "three")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y)
  .attr("width", bar3_target_width)
  .attr("height", bar_target_height);

threeBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "three_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar3_target_width)
  .attr("height", bar_label_height);
      
var fourBar = d3.select("svg").append("g")
  .attr("id", "fourBar")
  .style("display", "none");

fourBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "several")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y)
  .attr("width", bar4_target_width)
  .attr("height", bar_target_height);

fourBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "one_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar4_target_width)
  .attr("height", bar_label_height);

fourBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "daily")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar4_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y)
  .attr("width", bar4_target_width)
  .attr("height", bar_target_height);

fourBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "two_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar4_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar4_target_width)
  .attr("height", bar_label_height); 

fourBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "multiple")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar4_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y)
  .attr("width", bar4_target_width)
  .attr("height", bar_target_height);
  
fourBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "three_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar4_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar4_target_width)
  .attr("height", bar_label_height);

fourBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "weekly")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar4_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y)
  .attr("width", bar4_target_width)
  .attr("height", bar_target_height);

fourBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "three_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar4_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar4_target_width)
  .attr("height", bar_label_height);

var fiveBar = d3.select("svg").append("g")
  .attr("id", "fiveBar")
  .style("display", "none");

fiveBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "one")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y)
  .attr("width", bar5_target_width)
  .attr("height", bar_target_height);

fiveBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "one_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar5_target_width)
  .attr("height", bar_label_height);


fiveBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "two")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y)
  .attr("width", bar5_target_width)
  .attr("height", bar_target_height);

fiveBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "two_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar5_target_width)
  .attr("height", bar_label_height); 


fiveBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "three")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y)
  .attr("width", bar5_target_width)
  .attr("height", bar_target_height);

fiveBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "three_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar5_target_width)
  .attr("height", bar_label_height);


fiveBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "four")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y)
  .attr("width", bar5_target_width)
  .attr("height", bar_target_height);

fiveBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "four_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar5_target_width)
  .attr("height", bar_label_height);

fiveBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "five")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4)
  .attr("y", boxbar_offset_y)
  .attr("width", bar5_target_width)
  .attr("height", bar_target_height);

fiveBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "five_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar5_target_width)
  .attr("height", bar_label_height);

var sixBar = d3.select("svg").append("g")
  .attr("id", "sixBar")
  .style("display", "none");

sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "one")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "one_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height);


sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "two")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar6_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "two_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + bar6_target_width + boxbar_margin)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height); 


sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "three")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "three_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height);


sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "four")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "four_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height);

sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "five")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "five_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height);

sixBar.append("rect")
  .attr("class", "bar_target")
  .attr("id", "six")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5)
  .attr("y", boxbar_offset_y)
  .attr("width", bar6_target_width)
  .attr("height", bar_target_height);

sixBar.append("rect")
  .attr("class", "bar_label")
  .attr("id", "six_lab")     
  .attr("rx", 4)
  .attr("ry", 4)
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5)
  .attr("y", boxbar_offset_y - bar_label_height - boxbar_label_margin)
  .attr("width", bar6_target_width)
  .attr("height", bar_label_height);


// Boxes with labels
var relationship_labels = d3.select("svg").append("g")
  .attr("id", "relationship_labels")
  .style("display", "none")
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Partner")
  .attr("x", boxbar_offset_x + (bar6_target_width / 2) - ("Partner".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Een vriend/vriendin")
  .attr("x", boxbar_offset_x + bar6_target_width + boxbar_margin + (bar6_target_width / 2) - ("Een vriend/vriendin".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Familielid")
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2 + (bar6_target_width / 2) - ("Familielid".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Buurtgenoot")
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3 + (bar6_target_width / 2) - ("Buurtgenoot".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Collega") 
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4 + (bar6_target_width / 2) - ("Collega".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);
relationship_labels.append("text")
  .attr("class", "bar_text")
  .text("Anders") 
  .attr("x", boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5 + (bar6_target_width / 2) - ("Anders".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var relative_age_labels = d3.select("svg").append("g")
  .attr("id", "relative_age_labels")
  .style("display", "none")

relative_age_labels.append("text")
  .attr("class", "bar_text")
  .text("Veel jonger")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Veel jonger".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

relative_age_labels.append("text")
  .attr("class", "bar_text")
  .text("Jonger")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Jonger".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

relative_age_labels.append("text")
  .attr("class", "bar_text")
  .text("Ongeveer even oud")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Ongeveer even oud".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

relative_age_labels.append("text")
  .attr("class", "bar_text")
  .text("Ouder")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Ouder".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

relative_age_labels.append("text")
  .attr("class", "bar_text")
  .text("Veel ouder") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Veel ouder".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var education_labels = d3.select("svg").append("g")
  .attr("id", "education_labels")
  .style("display", "none")

education_labels.append("text")
  .attr("class", "bar_text")
  .text("Basisschool/middelbare school")
  .attr("x", boxbar_offset_x + (bar3_target_width / 2) - ("Basisschool/middelbare school".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

education_labels.append("text")
  .attr("class", "bar_text")
  .text("MBO")
  .attr("x", boxbar_offset_x + bar3_target_width + boxbar_margin + (bar3_target_width / 2) - ("MBO".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

education_labels.append("text")
  .attr("class", "bar_text")
  .text("HBO/universiteit")
  .attr("x", boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2 + (bar3_target_width / 2) - ("HBO/universiteit".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var frequency_labels = d3.select("svg").append("g")
  .attr("id", "frequency_labels")
  .style("display", "none")

frequency_labels.append("text")
  .attr("class", "bar_text")
  .text("Minder dan een keer per week")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Minder dan een keer per week".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

frequency_labels.append("text")
  .attr("class", "bar_text")
  .text("Een keer per week")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Een keer per week".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

frequency_labels.append("text")
  .attr("class", "bar_text")
  .text("Meerdere keren per week")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Meerdere keren per week".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

frequency_labels.append("text")
  .attr("class", "bar_text")
  .text("Om de dag")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Om de dag".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

frequency_labels.append("text")
  .attr("class", "bar_text")
  .text("Dagelijks") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Dagelijks".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var closeness_labels = d3.select("svg").append("g")
  .attr("id", "closeness_labels")
  .style("display", "none")

closeness_labels.append("text")
  .attr("class", "bar_text")
  .text("Helemaal niet hecht")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Helemaal niet hecht".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

closeness_labels.append("text")
  .attr("class", "bar_text")
  .text("Niet hecht")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Niet hecht".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

closeness_labels.append("text")
  .attr("class", "bar_text")
  .text("Een beetje hecht")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Een beetje hecht".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

closeness_labels.append("text")
  .attr("class", "bar_text")
  .text("Hecht")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Hecht".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

closeness_labels.append("text")
  .attr("class", "bar_text")
  .text("Heel hecht") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Heel hecht".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var compliance_labels = d3.select("svg").append("g")
  .attr("id", "compliance_labels")
  .style("display", "none")

compliance_labels.append("text")
  .attr("class", "bar_text")
  .text("Helemaal niet")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Helemaal niet".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

compliance_labels.append("text")
  .attr("class", "bar_text")
  .text("Een beetje")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Een beetje".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

compliance_labels.append("text")
  .attr("class", "bar_text")
  .text("Best wel")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Best wel".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

compliance_labels.append("text")
  .attr("class", "bar_text")
  .text("Strikt")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Strikt".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

compliance_labels.append("text")
  .attr("class", "bar_text")
  .text("Heel strikt") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Heel strikt".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var norms_labels = d3.select("svg").append("g")
  .attr("id", "norms_labels")
  .style("display", "none")

norms_labels.append("text")
  .attr("class", "bar_text")
  .text("Helemaal niet")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Helemaal niet".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

norms_labels.append("text")
  .attr("class", "bar_text")
  .text("Niet")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Niet".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

norms_labels.append("text")
  .attr("class", "bar_text")
  .text("Een beetje")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Een beetje".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

norms_labels.append("text")
  .attr("class", "bar_text")
  .text("Erg")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Erg".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

norms_labels.append("text")
  .attr("class", "bar_text")
  .text("Heel erg") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Heel erg".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

var social_sanctions_labels = d3.select("svg").append("g")
  .attr("id", "social_sanctions_labels")
  .style("display", "none")

social_sanctions_labels.append("text")
  .attr("class", "bar_text")
  .text("Helemaal niet waarschijnlijk")
  .attr("x", boxbar_offset_x + (bar5_target_width / 2) - ("Helemaal niet waarschijnlijk".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

social_sanctions_labels.append("text")
  .attr("class", "bar_text")
  .text("Niet waarschijnlijk")
  .attr("x", boxbar_offset_x + bar5_target_width + boxbar_margin + (bar5_target_width / 2) - ("Niet echt waarschijnlijk".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

social_sanctions_labels.append("text")
  .attr("class", "bar_text")
  .text("Een beetje waarschijnlijk")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + (bar5_target_width / 2) - ("Een beetje waarschijnlijk".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

social_sanctions_labels.append("text")
  .attr("class", "bar_text")
  .text("Waarschijnlijk")
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + (bar5_target_width / 2) - ("Waarschijnlijk".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

social_sanctions_labels.append("text")
  .attr("class", "bar_text")
  .text("Zeer waarschijnlijk") 
  .attr("x", boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + (bar5_target_width / 2) - ("Zeer waarschijnlijk".length * 3))
  .attr("y", boxbar_offset_y - boxbar_label_margin - 6);

restart();