cd(@__DIR__)


using SpecialFunctions
using Cubature
using BenchmarkTools
using Printf
using DelimitedFiles
using DataInterpolations
using FileIO

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

#function environment(n)
#    global n
#    if n ≈ 1.33
#        env = "wat"
#    elseif n ≈ 1
#        env = "air"
#    else
#        env = n
#    end
#    return env
#end


# Parameters for particles

#println("Ingrese los valores separados por comas:")
#L = parse.(Float64, split(readline(), ","))
Ls = [50, 80, 120, 150, 180, 200, 220]
Ls = [l * nm for l in Ls]
Rs = [3, 4, 5, 6]

r = [0, 0, 0]


#Implementar que calcule menos lambdas dependiendo de la posición del pico?. Elimine las que distan x del pico.

lam0 = 400 * nm
lam1 = 1600 * nm
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
    global sigma
    global alpha
    global folder_name


    mkdir( joinpath(folder_name, string(environment(t, ns))) )
    array = set_array(a, n, N, mode)
    
    let L, R = 0
    for material in materials
        (re_eps, im_eps) = add_eps(material, 1)

        for L in Ls
            for R in Rs
                #global L
                #global R
                global nlam
                global lam0
                global lam1
                local max_lam
                local max_sigma

                function name_datafile(folder_name, material, n, L, R, lam0, lam1, nlam)
                    @sprintf("%s_EAp_%s_%s__L%d_R%d__lam_%d_%d_%d.dat",folder_name, material, typeof(environment(t, ns)) <: AbstractString ? environment(t, ns) : string(environment(t, ns)), L / nm, R, lam0 / nm, lam1 / nm, nlam)
                end

                V = pi * (3 * R - 1) / (12 * R^3) * L^3 
                A = L/R * (L - L / R) + pi * (L / (2 * R))^2
              
                # Crear el nombre de archivo     #@sprintf: Return @printf formatted output as string.
                name_outfile = name_datafile(folder_name, material, n, L, R, lam0, lam1, nlam)                
                # Crear y escribir en el archivo
                fout0 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "w")
                @printf(fout0, "%-9s %-11s %-11s %-11s %-11s  %-25s %-25s %-25s  \n", "lam(nm)", "sext_t", "sext_l", "sabs_t", "sabs_l", "alpha_x", "alpha_y", "alpha_z")
                close(fout0)
                 
                max_sigma = -Inf
                max_lam = 0
                original_name = name_outfile

                function update_file_name(original_name, nlam, lam1) # Solo se actualiza para lam mayores
                    parts = split(original_name, "_")
                    parts[end-1:end-0] = [string(Int(round(lam1 / nm))), string(Int(round(nlam))) * ".dat"]
                    updated_name = join(parts, "_")
                    name_outfile_1 = mv(
                            joinpath(folder_name, string(environment(t, ns)), original_name),
                            joinpath(folder_name, string(environment(t, ns)), updated_name),
                            force=true)  
                    return updated_name
                end

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
                    sigma = calc_sigma(w, array, ucell[1])   # unica partícula de la cela unitat. Retorna 4 arguments
                    
                    
                    if sigma[2] > max_sigma  #Es la 3ra COLUMNA
                        
                        max_sigma = sigma[2]
                        max_lam = lam
                    end
                    #println(max_lam / nm)



                    #if (max_lam > lam1 - 200 * nm) || (sigma[2] > max_sigma) #Que no sustituya por completo, sino temporalemente para esta condición?
                    #    nlam = nlam + 200
                    #    lam1 = lam1 + 200 * nm
                    #    name_outfile = update_file_name(original_name, nlam, lam1)
                    #    fout1 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a")
                    #else 
                    fout1 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a")
                    #end


                    #println(L, ' ', R, " ", nlam)

                    output_str = @sprintf("%-10.3f", lam/nm)
                    output_str *= join([@sprintf("%-11.5e", sigma[s] * a^2 / A) for s in eachindex(sigma)], " ")
                    output_str *= "  "
                    output_str *= join([@sprintf("%-10.5e+%-10.5eim", real(alpha[p] / V), imag(alpha[p] / V)) for p in eachindex(alpha)], " ")
                    @printf(fout1, "%s\n", output_str)  
                    close(fout1)


                    
                    #fout_LR = open(folder_name,"El_LR_values" ,"w")
                    #@printf(fout_LR, "%-10s%-10s %s in %s \n", "L_values", "R_values", material, n)
                    #close(fout_LR)

                    #open(fout_LR)


                end


                #println(1, ' ', max_lam / nm,' ', max_sigma)
                #println(2, ' ', lam1 / nm,' ', nlam)              
                #print(3, ' ', lam1 / nm,' ', nlam)

                
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

end



#DUDA porque devidimos por la a^2 si al solo tener una partícula no es necesario