cd $HOME/codes/hgo_biomechanical_cardiac_model/  

edp="Resolution_2d_LR2.edp"
args=(2009 2025)

for a in "${args[@]}"; do
  echo "=== Running: FreeFem++ $edp $a ==="
  FreeFem++ "$edp" "$a"  > "Curta/logs/run_${a}.out"
done