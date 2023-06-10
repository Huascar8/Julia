cd(@__DIR__)


using SpecialFunctions
using Cubature
using BenchmarkTools
using Printf
using DelimitedFiles
using DataInterpolations


include("../code/lrop.jl")
include("../code/julia_lib/units.jl")
#Falta posar arguments!!!!
# Implementar ponerle una lista de lo que quiero calcular ex: S = [E,P]
#En base a las magnitudes calculdas, ponerlas en el nombre.
#Quiero crear un ST (total) que odene todos los archivos en subcarpetas según material, L, R, etc. Los calcule de nuevo, o copie o acceso directo de los de las anterioers carpetas.


materials=["Ag","Au"]

# Parameters array  . no es poden treure encara que no "s'utilitzin"

ns = [1, 1.33]
a = 400 * nm   #Necessari. Dividim el ouput entre l'area a^2 de la cela unitat
N = 1               #N is the number of particles in the unit cell
mode = 0

function environment(t, ns)
    env = ""
    if ns[Int(t)] ≈ 1.33
        env = "wat"
    elseif ns[Int(t)] ≈ 1
        env = "air"
    else
        env = ns[Int(t)]
    end
    return env
end

# Parameters for particles

#println("Ingrese los valores separados por comas:")
#L = parse.(Float64, split(readline(), ","))
Ls = [20, 50, 80, 100, 200]
Ls = [l * nm for l in Ls]
Rs = [3, 4, 5, 6]

r = [0, 0, 0]


#Implementar que calcule menos lambdas dependiendo de la posición del pico?. Elimine las que distan x del pico.

lam0 = 400 * nm
lam1 = 1200 * nm
nlam = 3000



function new_S_file()
    items = readdir() #Devuelve el nombre de cada carpeta
    folder_nums = [parse(Int, match(r"S(\d+)", item).captures[1]) for item in items if isdir(item) && occursin(r"S(\d+)", item)]
    if isempty(folder_nums)
        last_folder_num = 0
    else
        last_folder_num = maximum(folder_nums)
    end
    name = "S" * string(last_folder_num + 1)
    mkdir(name)
    return name
end

folder_name = new_S_file()



for (t, n) in enumerate(ns)
    mkdir( joinpath(folder_name, string(environment(t, ns))) )
    array = set_array(a, n, N, mode)
    for material in materials 
        (re_eps, im_eps) = add_eps(material, 1)
        for L in Ls
            for R in Rs
                 #No es necesario aquí. Poner en plots
                V = pi * (3 * R - 1) / (12 * R^3) * L^3 
                A = L/R * (L - L / R) + pi * (L / (2 * R))^2

                
                # Crear el nombre de archivo     @sprintf: Return @printf formatted output as string.
                name_outfile = @sprintf("%s_EiP_%s_%s__L%d_R%d__lam_%d_%d_%d.dat",folder_name, material, typeof(environment(t, ns)) <: AbstractString ? environment(t, ns) : string(environment(t,ns)), L / nm, R, lam0 / nm, lam1 / nm, nlam)
                
                # Crear y escribir en el archivo
                fout0 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "w")
                @printf(fout0, "%-9s %-11s %-11s %-11s %-11s  %-25s %-25s %-25s  \n", "lam(nm)", "sext_t", "sext_l", "sabs_t", "sabs_l", "alpha_x", "alpha_y", "alpha_z")
                close(fout0)
                
                max_sigma = -Inf
                max_lam = 0

                for i = 1:nlam
                    if i == 1
                        lam = lam0
                    else
                        lam = lam0 + (i - 1) * (lam1 - lam0) / (nlam - 1)
                    end
                    w = 2 * pi * c_au / lam  #Todo lo que está dentro del codigo está definido en unidades atomicas
                
                    particle = set_particle(r, L, R, re_eps(w), im_eps(w))
                    ucell = [particle]  #No cal. 'això no hauria de ser unit_cell ?? (no es necesario, es como lo definimos aqui)' 'array formado por la celda unidad que contiene una particula'
                    
                    alpha = get_alpha(w, array, ucell[1])
                    sigma = calc_sigma(w, array, ucell[1])   #'unica partícula de la cela unitat' 'Retorna 4 arguments'
                    

                    fout1 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a")
                    output_str = @sprintf("%-10.3f", lam/nm)
                    output_str *= join([@sprintf("%-11.5e", sigma[s] * a^2 / A) for s in eachindex(sigma)], " ")
                    output_str *= "  "
                    output_str *= join([@sprintf("%-10.5e+%-10.5eim", real(alpha[p] / V), imag(alpha[p] / V)) for p in eachindex(alpha)], " ")
                    @printf(fout1, "%s\n", output_str)
                    close(fout1) 
                    
                    if sigma[2] > max_sigma 
                        max_sigma = sigma[2]
                        max_lam = lam   
                    end

                end
                
                #Pic extinció
                fout2 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a+")  # Abrir el archivo en modo "append" (agregar contenido al final)
                seek(fout2, 0)
                existing_content = read(fout2, String)
                seek(fout2, 0)
                @printf(fout2, "#sext_max: %g, lam: %g\n%s", max_sigma * a^2 / A, max_lam/nm, existing_content)
                close(fout2)

            end
        end

    end
end






#DUDA porque devidimos por la a^2 si al solo tener una partícula no es necesario