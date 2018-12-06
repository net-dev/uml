cd %1
md %2
cd %2
dotnet new console
cd..
dotnet sln add %2/%2.csproj
cd..
