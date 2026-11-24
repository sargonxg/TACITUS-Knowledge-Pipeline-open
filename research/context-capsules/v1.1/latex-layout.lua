-- Let long source hashes wrap without adding hyphens or changing their value.
function Code(element)
  if FORMAT == "latex" and element.text:match("^[a-f0-9]+$") and
      (#element.text == 40 or #element.text == 64) then
    return pandoc.RawInline("latex", "\\texttt{\\seqsplit{" .. element.text .. "}}")
  end
end

-- The compact comparison tables fit on a page; keep their rows together.
function Table(element)
  if FORMAT == "latex" then
    return {pandoc.RawBlock("latex", "\\Needspace{20\\baselineskip}"), element}
  end
end

-- Keep the estimand's definition with its displayed equation.
function Para(element)
  if FORMAT == "latex" and pandoc.utils.stringify(element):match("^For paired task") then
    return {pandoc.RawBlock("latex", "\\Needspace{7\\baselineskip}"), element}
  end
end
