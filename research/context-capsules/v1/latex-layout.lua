-- Let long source hashes wrap without adding hyphens or changing their value.
function Code(element)
  if FORMAT == "latex" and element.text:match("^[a-f0-9]+$") and
      (#element.text == 40 or #element.text == 64) then
    return pandoc.RawInline("latex", "\\texttt{\\seqsplit{" .. element.text .. "}}")
  end
end
