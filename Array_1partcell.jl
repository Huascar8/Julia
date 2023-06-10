cd(@__DIR__)


using SpecialFunctions
using Cubature
using BenchmarkTools
using Printf
using DelimitedFiles
using DataInterpolations
using FileIO
using DelimitedFiles
using Base: walkdir


include("../code/lrop.jl")
include("../code/julia_lib/units.jl")
 

# Parameters array
a = 450 * nm
ns = [1, 1.33]
N = 1
mode = 0        #NO interaction

# Parameters convergence
NN = 4
maxes = [1 * 10^4, 1 * 10^5]
rtol = 0.1
et = 1

# Parameters light beam
mode_LB = 2
w0s = [8000 * nm]  # 'Varias veces el período. Ex. 100 veces'

# Parameters for particles
Ls = [80,120]
Ls = [l * nm for l in Ls]
Rs = [5,6]
r = [0, 0, 0]

materials=["Ag","Au"]




lam0 = 650 * nm
lam1 = 1150 * nm
nlam = 1000       #   'Optimizar. Pocas!' #1500


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
function new_R_file()
    items = readdir() #Devuelve el nombre de cada carpeta
    folder_nums = [parse(Int, match(r"R(\d+)", item).captures[1]) for item in items if isdir(item) && occursin(r"R(\d+)", item)]
    if isempty(folder_nums)
        last_folder_num = 0
    else
        last_folder_num = maximum(folder_nums)
    end
    name = "R" * string(last_folder_num + 1)
    mkdir(name)
    return name
end



folder_name = new_R_file()

for w0 in w0s
    LB = set_LB(2, w0) #
    for (t, n) in enumerate(ns)
        global sext_l
        global sigma
        global alpha
        global folder_name
        global Pt_abs
        global Pt_ext
        global a
        mkdir( joinpath(folder_name, string(environment(t, ns))) )

        let L, R, a, maxe = 0
        for material in materials
            #println(material)
            (re_eps, im_eps) = add_eps(material, 1) #
            for L in Ls
                for R in Rs
                    global nlam
                    global lam0
                    global lam1
                    local max_lam
                    local max_sigma
                    V = pi * (3 * R - 1) / (12 * R^3) * L^3 
                    A = L/R * (L - L / R) + pi * (L / (2 * R))^2


                    data_files_path = String[]
                    #file_path = String[]
                    let root, dirs, files = ""
                    for (root, dirs, files) in walkdir(@__DIR__)
                        let file = String[]
                        for file in files
                            file_path = joinpath(root, file)
                            #println(file_path)
                            if endswith(String(file), ".dat") && startswith(string(file), "S3_EAp_$(material)_$(environment(t, ns))__L$(Int(L/nm))_R$(R)__") #Definirlo a partir de una funcion ?
                                push!.(Ref(data_files_path), file_path) #push!(data_files, file_path) esto tambien funciona
                                #println(file)
                            end 
                        end
                    end end
                    #println(files) # No imprime nada
                    end 
                    println(data_files_path)
                    #    if occursin(".dat", path) && !isdir(path) && startswith(basename(path), "S1_EiP_$(material)_$(n)__L$(L)_R$(R)__") #Está mal

                    flag = false
                    if !isempty(data_files_path)
                        open(data_files_path[1]) do file  
                            first_line = readline(file)
                            println(first_line)
                            data = readdlm(file, ' ', skipstart=1)
                            sext_l = data[:, 5]  #Que no tenga que tener en cuenta el numero de espacios entre columnas??
                            sabs_l = data[:, 7]
                            alpha_z = data[:, 11]
                            flag = true
                            match_result = match(r"lam: ([\d.]+)", first_line) #Cambiarlo
                            println(match_result)
                            if match_result !== nothing
                                a = parse(Float64, match_result.captures[1]) / n * nm
                                print(a)
                                #Int(round(a))
                            end
                        end
                    else
                        println("No such file!")
                        #local a = a  #   NOSEE
                    end

                    #lambdas...



                    Range_a = collect(range(a - 10 * nm, a + 10 * nm, length=3))

                    for a in Range_a
                        array = set_array(a, n, N, mode) #
                        #println(array)

                        for maxe in maxes
                            println(w0/nm)
                            conv = set_conv(NN, maxe, rtol, et) #
                            #println(conv)
                            function name_datafile(folder_name, material, n, L, R, w0, a, NN, maxe, lam0, lam1, nlam)
                                @sprintf("%s_PaPeExtElpz_%s_%s__L%d_R%d__w%d__a%d_NN%d_maxe%d__lam_%d_%d_%d.dat", folder_name, material, typeof(environment(t, ns)) <: AbstractString ? environment(t, ns) : string(environment(t, ns)), L / nm, R, Int(round(w0/nm)), a/nm, NN, maxe, lam0 / nm, lam1 / nm, nlam)
                            end

                            name_outfile = name_datafile(folder_name, material, n, L, R, w0, a, NN, maxe, lam0, lam1, nlam)
                            
                            fout0 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "w")
                            @printf(fout0, "%-9s %-11s %-11s  %-11s %-11s  %-11s %-11s %-11s   %-11s %-11s %-25s  \n", "lam(nm)", "Pt_abs", "erPt_abs", "Pt_ext", "erPt_ext", "ext_x", "ext_y", "ext_z", "sabs_l", "sext_l", "alpha_z")
                            close(fout0)
                            
                            max_Ptabs = -Inf
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
                                #println(w, array, ucell, LB, conv)


                                Pt_abs, erPt_abs = calc_Pt(w, array, ucell, LB, conv) # '(Pt,erPt)'
                                Pt_ext, erPt_ext = calc_Pt_ext(w, array, ucell, LB, conv) #'(Pt_ext,erPt_ext)'
                                ext = calc_ext(w, [0,0], array, ucell, conv)

                                sext_l  = calc_sigma(w, array, ucell[1])[2]  # unica partícula de la cela unitat.
                                sabs_l  = calc_sigma(w, array, ucell[1])[4]
                                alpha_z = get_alpha(w, array, ucell[1])[3]

                                
                                if  Pt_abs> max_Ptabs 
                                    max_Ptabs = Pt_abs
                                    max_lam   = lam
                                end

                                #if (max_lam > lam1 - 200 * nm) || (Pt_abs[21 > max_Ptabs) #Que no sustituya por completo, sino temporalemente para esta condición?
                                #    nlam = nlam + 200
                                #    lam1 = lam1 + 200 * nm
                                #    name_outfile = update_file_name(original_name, nlam, lam1)
                                #    fout1 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a")
                                #else 
                                fout1 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a")
                                #end

                                output_str = @sprintf("%-10.3f", lam/nm)          #      'Entre A ???'
                                output_str *= join([@sprintf("%-11.5e", Pt_abs), @sprintf("%-11.5e", erPt_abs)],  " ")
                                output_str *= "  "
                                output_str *= join([@sprintf("%-11.5e", Pt_ext), @sprintf("%-11.5e", erPt_ext)],  " ")
                                output_str *= "  "
                                output_str *= join([@sprintf("%-11.5e", ext[s] * a^2 / A) for s in eachindex(ext)], " ")
                                output_str *= "   "
                                output_str *= @sprintf("%-11.5e", sext_l * a^2 / A) #Cuidado espacios
                                output_str *= " "
                                output_str *= @sprintf("%-11.5e", sabs_l * a^2 / A)
                                output_str *= " "
                                output_str *= @sprintf("%-10.5e+%-10.5eim", real(alpha_z / V), imag(alpha_z / V))
                                @printf(fout1, "%s\n", output_str)
                                close(fout1)
                            end

                            fout2 = open(joinpath(folder_name, string(environment(t, ns)), name_outfile), "a+")  # Abrir el archivo en modo "append" (agregar contenido al final)
                            seek(fout2, 0)
                            existing_content = read(fout2, String)
                            seek(fout2, 0)
                            @printf(fout2, "Ptabs_max = %g,   lam = %g\n%s", max_Ptabs, max_lam/nm, existing_content)
                            close(fout2)

                        end
                    end


                    
                end
            end
        end
        end
    end
end