#!/usr/bin/ruby
#!/opt/local/bin/ruby

# sbatch -N 1 -o HIDDEN_FITS_SCAN_p2 -t 48:00:00 -p RM ./hidden.rb
require 'parallel'

prefix="/jet/home/sdedeo/humanities-glass/data/clean/"
new_prefix="/jet/home/sdedeo/humanities-glass/data/mdl_experiments/"

ans=[2.0].collect { |p_norm|
  
  [0,1,2,3].collect { |hidden|

    filename=`ls #{prefix}`.split("\n").select { |filename|
      filename_out=filename+".mpf_p=#{p_norm}"

      n_lines=`wc -l #{prefix+filename}`.split(" ")[0].to_i
      n=filename.split("_")[2].to_i
      num_na=filename.split("_")[4].to_i

      (n == 20) and (num_na == 5)
    }[0]

    n_lines=`wc -l #{prefix+filename}`.split(" ")[0].to_i
    n=filename.split("_")[2].to_i
    num_na=filename.split("_")[4].to_i

    print "Doing #{filename} at #{Time.now} with #{p_norm} and #{hidden} hidden nodes\n"
    filename_out=filename+".mpf"+"p=#{p_norm}_hidden#{hidden}"

    file=File.new(prefix+filename, 'r')
    str=""
    file.each_line { |set|
      str << ("X"*hidden)+set.split(" ")[0..-2].collect { |i| (i.to_i == 0) ? "X" : ((i.to_i < 0) ? "0" : "1") }.join()+" "+set.split(" ")[-1]+"\n"
    }
    file.close
    file_out=File.new(new_prefix+filename_out, 'w')
    file_out.write("#{n_lines}\n#{n+hidden}\n")
    file_out.write(str); file_out.close

    ans=`OMP_NUM_THREADS=128 ./mpf -c #{new_prefix+filename_out} #{p_norm}`
    print "FINAL VERSION for #{filename_out}:\n #{ans}\n\n"

    sparsity=ans.scan(/Best\ log\_sparsity\:[^\n]+\n/)[0].split(" ")[-1].to_f
    logl=ans.scan(Regexp.new(Regexp.escape(sparsity.to_s)+"[^\\n]+\\n"))[0].split(" ")[-1].to_f
    overall=ans.scan(/parameters\:[^\n]+\n/)[0].split(" ")[-1].to_f
    print "FINISHED AT #{Time.now}\n"

    ans=[p_norm, hidden, sparsity, logl, overall]
    print "#{ans}\n"

    final=Parallel.map(Array.new(128) { |i| i },  :in_process=>128) { |proc|
      ans=`./mpf -l #{new_prefix+filename_out} #{sparsity} #{p_norm}`
    }

    outcome=[p_norm, hidden] + final.collect { |ans| 
      [eval(ans.split("\n").select { |i| i.include?("params") }[0]), ans.scan(/parameters\:[^\n]+\n/)[0].split(" ")[-1].to_f]
    }.sort { |i,j| j[1] <=> i[1] }
    
    print "#{outcome}\n"
    outcome
  }
  
}

print "#{ans}\n"