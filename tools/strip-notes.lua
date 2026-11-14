-- Public build: drop speaker notes so the published deck carries none.
-- Active only under the "public" profile (_quarto-public.yml).
function Div(el)
  if el.classes:includes("notes") then
    return {}
  end
end
