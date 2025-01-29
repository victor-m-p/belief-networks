<?php


  $fp = fopen('results/data.csv', 'a');

  fputcsv($fp, $_POST);
  
  fclose($fp);
?>
