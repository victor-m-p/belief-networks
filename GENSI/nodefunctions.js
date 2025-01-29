//---------------------------------------------
// Declaration of functions for nodes and links
//---------------------------------------------

// Graph iteration
function tick(e) {
  
  link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  var k = e.alpha;

  // Push nodes toward their designated focus.
  nodes.forEach(function(o, i) {
    if(!o.fixed) {
      o.y += (foci[o.id].y - o.y) * k;
      o.x += (foci[o.id].x - o.x) * k;
    }
  });

  node.attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; })
      .attr("name", function(d) { return d.name; })
      .attr("id", function(d) { return d.id; })
      .attr("race", function(d) { return d.race; })
      .attr("edu", function(d) { return d.edu; })
      .attr("freq", function(d) { return d.freq; })
      .attr("male", function(d) { return d.male; })
      .attr("healthcare_worker", function(d) { return d.healthcare_worker; })
      .attr("trustworthy", function(d) { return d.trustworthy; })
      .attr("risk_group", function(d) { return d.risk_group; })
      .attr("infected", function(d) { return d.infected; })
      .attr("transform", function(d){return "translate("+d.x+","+d.y+")"});

  if (currSlide == 8 || currSlide == 11 || currSlide == 12 || (currSlide < 23 && currSlide > 15) || currSlide == 25) {
    d3.selectAll(".node").style("fill", function(d) { 
      if (d.x > boxbar_offset_x
       && d.x < boxbar_offset_x + bar5_target_width
       && d.y > boxbar_offset_y
       && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[0];
      } else if (d.x > boxbar_offset_x + bar5_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar5_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[1];
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[2];
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[3];
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[4];
      } else {
        if (d.name == "Uzelf") {
          return selfColor;
        } else {
          return nodeColor;
        }
        
      }
    });
  } else if (currSlide == 9) {
    d3.selectAll(".node").style("fill", function(d) { 
      if (d.x > boxbar_offset_x
       && d.x < boxbar_offset_x + bar3_target_width
       && d.y > boxbar_offset_y
       && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[0];
      } else if (d.x > boxbar_offset_x + bar3_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar3_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[1];
      } else if (d.x > boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2 + bar3_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[2];
      } else {
        return nodeColor;
      }
    });
  } else if (currSlide == 6) {
    d3.selectAll(".node").style("fill", function(d) { 
      if (d.x > boxbar_offset_x
       && d.x < boxbar_offset_x + bar6_target_width
       && d.y > boxbar_offset_y
       && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[0];
      } else if (d.x > boxbar_offset_x + bar6_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar6_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[1];
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[2];
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[3];
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[4];
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        return answerColors[5];
      } else {
        return nodeColor;
      }
    });
  }
}

function altersInBoxes(n, include_self) {
  if (n == 3) {
    var hit = 0;
    nodes.forEach(function(d) { 
      if (d.x > boxbar_offset_x
      && d.x < boxbar_offset_x + bar3_target_width
      && d.y > boxbar_offset_y
      && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + bar3_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar3_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2 + bar3_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } 
    });
  } else if (n == 4) {
    var hit = 0;
    nodes.forEach(function(d) { 
      if (d.x > boxbar_offset_x
      && d.x < boxbar_offset_x + bar4_target_width
      && d.y > boxbar_offset_y
      && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + bar4_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar4_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar4_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar4_target_width + boxbar_margin) * 2 + bar4_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar4_target_width + boxbar_margin) * 3
              && d.x < boxbar_offset_x + (bar4_target_width + boxbar_margin) * 3 + bar4_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } 
    });
  } else if (n == 5) {
    var hit = 0;
    nodes.forEach(function(d) { 
      if (d.x > boxbar_offset_x
      && d.x < boxbar_offset_x + bar5_target_width
      && d.y > boxbar_offset_y
      && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + bar5_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar5_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4
              && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + bar5_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      }
    });
  } else if (n == 6) {
    var hit = 0;
    nodes.forEach(function(d) { 
      if (d.x > boxbar_offset_x
      && d.x < boxbar_offset_x + bar6_target_width
      && d.y > boxbar_offset_y
      && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + bar6_target_width + boxbar_margin
              && d.x < boxbar_offset_x + bar6_target_width * 2 + boxbar_margin
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5
              && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5 + bar6_target_width
              && d.y > boxbar_offset_y
              && d.y < boxbar_offset_y + bar_target_height) {
        hit++;
      }
    });
  }
  if (include_self) {
    return (hit == (numAlters + 1));
  } else {
    return (hit == numAlters);
  }
  
}

function saveAltersInBoxes(q, n, include_self) {
  start = 1;
  console.log(include_self)
  if (include_self) {
    start -= 1;
  }
  for (i = start; i <= numAlters; i++) {
    keys.push("q" + q + "_0" + i);
  }
  if (n == 3) {
    nodes.forEach(function(d) { 
      if (!include_self && d.id == 0) {
        return
      }
      if (d.id >= 0 && d.id <= numAlters) {
        if (d.x > boxbar_offset_x
         && d.x < boxbar_offset_x + bar3_target_width
         && d.y > boxbar_offset_y
         && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 1;
        } else if (d.x > boxbar_offset_x + bar3_target_width + boxbar_margin
                && d.x < boxbar_offset_x + bar3_target_width * 2 + boxbar_margin
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 2;
        } else if (d.x > boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2
                && d.x < boxbar_offset_x + (bar3_target_width + boxbar_margin) * 2 + bar3_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 3;
        } else {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;            
        }
      } else if (d.id > numAlters) {
        answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;
      }
    });

  } else if (n == 4) {

  } else if (n == 5) {
    nodes.forEach(function(d) { 
      if (!include_self && d.id == 0) {
        return
      }
      if (d.id >= 0 && d.id <= numAlters) {
        if (d.x > boxbar_offset_x
         && d.x < boxbar_offset_x + bar5_target_width
         && d.y > boxbar_offset_y
         && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 1;
        } else if (d.x > boxbar_offset_x + bar5_target_width + boxbar_margin
                && d.x < boxbar_offset_x + bar5_target_width * 2 + boxbar_margin
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 2;
        } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2
                && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 2 + bar5_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 3;
        } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3
                && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 3 + bar5_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 4;
        } else if (d.x > boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4
                && d.x < boxbar_offset_x + (bar5_target_width + boxbar_margin) * 4 + bar5_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 5;
        } else {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;            
        }
      } else if (d.id > numAlters) {
        answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;
      }
    });
  } else if (n == 6) {
    nodes.forEach(function(d) { 
      if (!include_self && d.id == 0) {
        return
      }
      if (d.id >= 0 && d.id <= numAlters) {
        if (d.x > boxbar_offset_x
         && d.x < boxbar_offset_x + bar6_target_width
         && d.y > boxbar_offset_y
         && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 1;
        } else if (d.x > boxbar_offset_x + bar6_target_width + boxbar_margin
                && d.x < boxbar_offset_x + bar6_target_width * 2 + boxbar_margin
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 2;
        } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2
                && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 2 + bar6_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 3;
        } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3
                && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 3 + bar6_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 4;
        } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4
                && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 4 + bar6_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 5;
        } else if (d.x > boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5
                && d.x < boxbar_offset_x + (bar6_target_width + boxbar_margin) * 5 + bar6_target_width
                && d.y > boxbar_offset_y
                && d.y < boxbar_offset_y + bar_target_height) {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = 6;
        } else {
          answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;            
        }
      } else if (d.id > numAlters) {
        answers['q'+ q + "_" + d.id.toLocaleString(undefined,{minimumIntegerDigits: 2})] = undefined;
      }
    });
  }
  
}

// Add node to graph
function addAlter() {
  var alterName = document.getElementById("alterName");

  if (alterName.value.length > 20 || alterName.value == " ") {
    promptOnlyOne();

  } else if (alterName.value.length > 0) {

    if (numAlters == 0) {

      document.getElementById("first_friend_text").style.display = "none";
      //document.getElementById("second_friend_text").style.display = "block";
    }

    if (numAlters == 7) {
      //document.getElementById("second_friend_text").style.display = "none";
      document.getElementById("final_friend_text").style.display = "block";
      document.getElementById("one_at_a_time").style.display = "none";

      document.getElementById("name_input").style.display = "none";
    }

    numAlters++;

    var d = new Date();
    if (numAlters <= 8) {
      nodes[numAlters].name = alterName.value;
      answers["q2_" + numAlters.toLocaleString(undefined,{minimumIntegerDigits: 2})] = alterName.value;
      // answers["q2_" + numAlters.toLocaleString(undefined,{minimumIntegerDigits: 2}) + "timeStamp"] = (d - startTime) / 1000;
      d3.selectAll(".node_text").text(function(d) { return d.name });
      d3.selectAll(".node").attr("opacity", function(d) { return d.index <= numAlters ? 1 : .4 });
    }

    document.getElementById("alterName").value = '';
  }
}

// Whenever nodes or links are added or changes are made to their properties, the graph needs to be restarted
function restart() {
  force.start();

  link = link.data(links);

  link.enter().insert("line", ".node")
      .attr("class", "link")
      .on("contextmenu", removeLink);

  link.exit().remove();

  node = node.data(nodes);

  var n = node.enter().append("svg:g")
    .attr("class", "node")
    .call(force.drag);

  n.append("svg:circle")
    .attr("class", "node")
    .attr("r", 25)
    .on("click", nodeSelect)
    .call(force.drag);

  n.append("svg:text")
    .attr("class", "node_text")
    .attr("text-anchor", "middle")  
    .attr("dy", ".3em")
    .attr("pointer-events", "none")
    .text(function(d) { return d.name });

  node.exit().remove();
}

// Reset foci to optimal positions
function resetFoci(include_self) {
  console.log("numalters: " + numAlters)
  for(i = 0; i <= 8; i++) {
    if(i > numAlters) {
      foci[i].x += 5000;
    } else {
      if (include_self) {
        foci[i].x = i*(bodyWidth/(numAlters + 1))-(bodyWidth/(numAlters + 1))/2 + 160;
      } else {
        foci[i].x = 1.1*(i*(bodyWidth/numAlters)-(bodyWidth/numAlters)/2 - 50);
      }
      
      if ((bodyWidth/numAlters)+(bodyWidth/(numAlters)) > 250) {
        foci[i].y = nodeLine;
      } else if ((bodyWidth/numAlters)+(bodyWidth/(numAlters)) < 125) {
        foci[i].y = nodeLine+(i % 3)*40;
      } else {
        foci[i].y = nodeLine+(i % 2)*40;
      }
    }
  }
  restart();
}

// Remove link between two nodes
function removeLink(l) {
  // Slide 7: draw links between friends that know each other 
  if (currSlide == 15) {
    links.splice(links.indexOf(l), 1);
    restart();
  }
}

function removeNode(n) {
    // nodes.splice(nodes.indexOf(n), 1);
    restart();
}

var selected = false;
var targetId;
var sourceId;

// Handles node selections depending on the current slide
function nodeSelect(d) {
  // Slide 15: select female alters
  if (currSlide == 7) {
    altered = true;
    if (d.name != "U") {
      if (d.male == true) {
        d3.select(this).style("fill", nodeColor)
        foci[d.id].y += 100;
        d.male = false;
      } else {
        d3.select(this).style("fill", maleColor)
        d.male = true;
        //foci[d.id].py = foci[d.id].y;
        foci[d.id].y -= 100;
      }
    }
    restart();
  }

  if (currSlide == 10) {
    altered = true;
    if (d.name != "U") {
      console.log(d.healthcare_worker);
      if (d.healthcare_worker == false) {
        d3.select(this).style("fill", maleColor)
        foci[d.id].y -= 100;
        d.healthcare_worker = true;
      } else {
        d3.select(this).style("fill", nodeColor)
        d.healthcare_worker = false;
        //foci[d.id].py = foci[d.id].y;
        foci[d.id].y += 100;
      }
    }
    restart();
  }
  if (currSlide == 13) {
    altered = true;
    if (d.name != "U") {
      if (d.trustworthy == false) {
        d3.select(this).style("fill", maleColor)
        foci[d.id].y -= 100;
        d.trustworthy = true;
      } else {
        d3.select(this).style("fill", nodeColor)
        d.trustworthy = false;
        //foci[d.id].py = foci[d.id].y;
        foci[d.id].y += 100;
      }
    }
    restart();
  }

  if (currSlide == 23) {
    altered = true;
    
    if (d.risk_group == false) {
      d3.select(this).style("fill", maleColor)
      foci[d.id].y -= 100;
      d.risk_group = true;
    } else {
      if (d.name == "Uzelf") {
        d3.select(this).style("fill", selfColor)
      } else {
        d3.select(this).style("fill", nodeColor)
      }
      d.risk_group = false;
      //foci[d.id].py = foci[d.id].y;
      foci[d.id].y += 100;
    }
    
    restart();
  }

  if (currSlide == 24) {
    altered = true;
    
    if (d.infected == false) {
      d3.select(this).style("fill", maleColor)
      foci[d.id].y -= 100;
      d.infected = true;
    } else {
      if (d.name == "Uzelf") {
        d3.select(this).style("fill", selfColor)
      } else {
        d3.select(this).style("fill", nodeColor)
      }
      d.infected = false;
      //foci[d.id].py = foci[d.id].y;
      foci[d.id].y += 100;
      
    }
    restart();
  }

  

  // Slide 7: draw links between friends that know each other 
  if (currSlide == 15) {
    var targetIndex = nodes[askedAbout].id;
    var sourceIndex = d.id;

    if(sourceIndex > targetIndex)

    if(!nodes[askedAbout][sourceIndex]){
      nodes[askedAbout][sourceIndex] = 1;
      //nodes[sourceIndex][askedAbout] = 1;
      links.push({source: sourceIndex, target: targetIndex});
    } else {
      nodes[askedAbout][sourceIndex] = 0;
      //nodes[sourceIndex][askedAbout] = 0;
      links.forEach(function(l) {
        if((l.source.id == sourceIndex || l.target.id == sourceIndex) && 
           (l.source.id == targetIndex || l.target.id == targetIndex))
        {
          removeLink(l);
        }
      });
    }

    /*if (selected == false) {
      targetId = d.id;
      console.log("targetId: " + targetId);
      selected = true;
    } else {
      sourceId = d.id;
      console.log("sourceid: " + sourceId);
      if (targetId != sourceId) {
        nodes.forEach(function(n) {
          if (n.id == targetId) {
            targetIndex = n.index;
            console.log("target: " + targetIndex);
          } else if (n.id == sourceId) {
            sourceIndex = n.index;
            console.log("source: " + sourceIndex);
          } 
        });
        nodes[sourceIndex].friendsWith += targetIndex.toString();
        nodes[targetIndex].friendsWith += sourceIndex.toString();
        links.push({source: sourceIndex, target: targetIndex});
      }
      selected = false;
    }*/
    restart();
  }
}

// Makes all nodes default color
function clearColors() {
  d3.selectAll(".node").style("fill", function(d) { if (d.name == "Uzelf") { return selfColor; } else { return nodeColor; } })
}