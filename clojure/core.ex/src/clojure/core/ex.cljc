(ns 
  ^{:doc 
    "
  * cum: Accumulatively calculate by function f and get a sequence.
  * update: Read, delete and modify collection function."}
  clojure.core.ex
  (:require [clojure.core.ex.xupdate]
            [clojure.core.ex.xapply]
            [clojure.core.ex.xfilter]
            [clojure.core.ex.concat-distinct]
            [clojure.core.ex.hiccup]
            [clojure.core.seq-func-extend :as sextend]))

(defmacro str? [s] `(string? ~s))

(defmacro cf [coll] `(first ~coll))
(defmacro cn [coll] `(next ~coll))
(defmacro cff [coll] `(-> ~coll first first))
(defmacro cfn [coll] `(-> ~coll first next))
(defmacro cnf [coll] `(-> ~coll next first))
(defmacro cnn [coll] `(-> ~coll next next))
(defmacro cfff [coll] `(-> ~coll first first first))
(defmacro cffn [coll] `(-> ~coll first first next))
(defmacro cfnf [coll] `(-> ~coll first next first))
(defmacro cfnn [coll] `(-> ~coll first next next))
(defmacro cnff [coll] `(-> ~coll next first first))
(defmacro cnfn [coll] `(-> ~coll next first next))
(defmacro cnnf [coll] `(-> ~coll next next first))
(defmacro cnnn [coll] `(-> ~coll next next next))
(defmacro cffff [coll] `(-> ~coll first first first first))
(defmacro cfffn [coll] `(-> ~coll first first first next))
(defmacro cffnf [coll] `(-> ~coll first first next first))
(defmacro cffnn [coll] `(-> ~coll first first next next))
(defmacro cfnff [coll] `(-> ~coll first next first first))
(defmacro cfnfn [coll] `(-> ~coll first next first next))
(defmacro cfnnf [coll] `(-> ~coll first next next first))
(defmacro cfnnn [coll] `(-> ~coll first next next next))
(defmacro cnfff [coll] `(-> ~coll next first first first))
(defmacro cnffn [coll] `(-> ~coll next first first next))
(defmacro cnfnf [coll] `(-> ~coll next first next first))
(defmacro cnfnn [coll] `(-> ~coll next first next next))
(defmacro cnnff [coll] `(-> ~coll next next first first))
(defmacro cnnfn [coll] `(-> ~coll next next first next))
(defmacro cnnnf [coll] `(-> ~coll next next next first))
(defmacro cnnnn [coll] `(-> ~coll next next next next))


(defn xor 
  ([x v] (or (and x (not v)) (and (not x) v)))
  ([x v & more] (apply xor (xor x v) more)))
(def nxor (complement xor))


;=====================================================================================================
;====  pipeline
;=====================================================================================================
(defmacro x->
  "Threads the expr through the forms. Inserts x as the
  second item in the first form, making a list of it if it is not a
  list already. If there are more forms, inserts the first form as the
  second item in second form, etc."
  {:added "1.0"}
  [x & forms]
  (loop [x x, forms forms]
    (if forms
      (let [form (first forms)
            threaded (if (seq? form)
                       (with-meta `(~(first form) ~x ~@(next form)) (meta form))
                       (list form x))]
        (if (= form 'x->>) 
          (apply list 'x->> x (next forms))
          (recur threaded (next forms))))
        
      x)))

(defmacro x->>
  "Threads the expr through the forms. Inserts x as the
  last item in the first form, making a list of it if it is not a
  list already. If there are more forms, inserts the first form as the
  last item in second form, etc."
  {:added "1.1"}
  [x & forms]
  (loop [x x, forms forms]
    (if forms
      (let [form (first forms)
            threaded (if (seq? form)
              (with-meta `(~(first form) ~@(next form)  ~x) (meta form))
              (list form x))]
        (if (= form 'x->) 
          (apply list 'x-> x (next forms))
          (recur threaded (next forms))))
      x)))
      
;=====================================================================================================
;====  sequential function extend
;=====================================================================================================
(defmacro seq-func-extend [func & bys] `(sextend/seq-func-extend ~func ~bys))
(defmacro pred-proc [func pred & colls] `(sextend/pred-proc ~func ~pred ~@colls))


(sextend/seq-func-extend take-while)
(sextend/seq-func-extend drop-while)
(sextend/seq-func-extend split-with)
(sextend/seq-func-extend partition-by)
(sextend/seq-func-extend filter)
(sextend/seq-func-extend remove)
(sextend/seq-func-extend some)


(def xfilter clojure.core.ex.xfilter/xfilter)
(def xapply clojure.core.ex.xapply/xapply)
(def concat-distinct clojure.core.ex.concat-distinct/concat-distinct)

(def transform clojure.core.ex.xupdate/transform)
(def xupdate clojure.core.ex.xupdate/xupdate)
(def %> clojure.core.ex.xupdate/%>)
(def %% clojure.core.ex.xupdate/%%)

(def hiccup2clj clojure.core.ex.hiccup/hiccup2clj)
(def clj2hiccup clojure.core.ex.hiccup/clj2hiccup)
;-----------------------------------------------------------------------------------
; SUB

(defn- xsub-position-type [coll pos]
  (cond
    (vector? coll) (get coll pos)
    (or (string? coll)
        (seq? coll)) (nth coll pos)
    (coll? coll) (loop [n pos c coll]
                   (if (zero? n)
                     (first c)
                     (recur (dec n) (next c))))
    :else nil))

(defn- xsub-position [{:keys [default-val]} coll pos]
  (when (and (or (coll? coll)
                 (string? coll))
             (integer? pos))
    (let [size (count coll)
          pos (if (< pos 0) (+ pos size) pos)]
      (if (or (< pos 0) (>= pos size))
        (if (= nil default-val)
          (throw (Exception. "Not found"))
          default-val)
        (xsub-position-type coll pos)))))

(defn- xsub-map [{:keys [default-val]} map key]
  (when (map? map)
    (if (contains? map key)
      (get map key)
      (if default-val
        default-val
        (throw (Exception. "Not found"))))))

(defn- sub-scope-position
  ([coll st]
   (cond (string? coll) (subs coll st)
         (vector? coll) (subvec coll st)
         (or (map? coll) (set? coll))
         (loop [s coll n 0 rst {}]
           (cond (< n st) (recur (next s) (inc n) {})
                 :else s))
         (seq? coll) (take-last (- (count coll) st) coll)))
  ([coll st ed]
   (cond (string? coll) (subs coll st ed)
         (vector? coll) (subvec coll st ed)
         (or (map? coll) (set? coll))
         (loop [s coll n 0 rst {}]
           (cond (< n st) (recur (next s) (inc n) {})
                 (and (>= n st) (< n ed)) (recur (next s) (inc n) (conj {} (first s)))
                 :else rst))
         (seq? coll) (let [len (count coll)] (->> coll (take-last (- len st)) (drop-last (- len ed)))))))

(defn- xsub-scope [{:keys [default-val]} coll a b]
  nil)

#_(defn- sub

   ([coll func default pos]
    #_(println coll " | " func " | " default " | " pos)
    (cond
      (= pos :SUB-CFG) coll
      (= pos :SUB-ONE) coll
      (= pos :SUB-SET) coll
      (= pos :SUB-MAP) coll
      (= func xsub-position) (func default coll pos)
      (= func xsub-scope) (func default coll pos -1)
      (= func xsub-map) (func default coll pos)
      :else (throw (Exception. (str {:coll coll :func func :default default :pos pos})))))

   ([coll func default pos more]
    #_(println coll " | " func " | " default " | " pos " | " more)
    (cond
      (= pos :SUB-CFG) coll
      (= pos :SUB-ONE) (sub coll xsub-position default more)
      (= pos :SUB-SET) (sub coll xsub-scope default more -1)
      (= pos :SUB-MAP) (sub coll xsub-map default more)
      (= func xsub-position) (sub (xsub coll func default pos) func default more)
      (= func xsub-scope) (sub coll func default pos more)
      (= func xsub-map) (sub (xsub coll func default pos) func default more)
      :else (throw (Exception. (str {:coll coll :func func :default default :pos pos :more more})))))

   ([coll func default pos pos2 & more]
    #_(println coll " | " func " | " default " | " pos " | " pos2 " | " more)
    (cond
      (= pos :SUB-CFG) (apply sub coll func pos2 more)
      (= pos :SUB-ONE) (apply sub coll xsub-position default pos2 more)
      (= pos :SUB-SET) (apply sub coll xsub-scope default pos2 more)
      (= pos :SUB-MAP) (apply sub coll xsub-map default pos2 more)
      (= func xsub-position) (apply sub (xsub coll func default pos) func default pos2 more)
      (= func xsub-scope) (apply sub (xsub coll func default pos pos2) func default more)
      (= func xsub-map) (apply sub (xsub coll func default pos) func default pos2 more)
      :else (throw (Exception. (str {:coll coll :func func :default default :pos pos :pos2 pos2 :more more}))))))

#_(defn xsub
   ([coll] (first coll))
   ([a b] (xsub b xsub-position {} a))
   ([a b & params]
    (let [coll (last params)
          params (butlast params)]
      (apply xsub coll xsub-position {} a b params))))

#_(defn xsubm
   ([key coll] (xsub-map {} coll key))
   ([a b & params]
    (let [coll (last params)
          params (butlast params)]
      (apply xsub coll xsub-map {} a b params))))

#_(defn xsubs
   ([coll] (next coll))
   ([a coll] (xsub coll xsub-scope {} a -1))
   ([a b & params] (let [coll (last params)
                         params (butlast params)]
                    (apply xsub coll xsub-scope {} a b params))))
;-----------------------------------------------------------------------------------




; bit-width
;---------------------------------------------------------------------------
(defn bit-width [size]
  (if (== size 1)
    1
    (as-> size x (Math/log x) (/ x (Math/log 2)) (Math/ceil x) (int x))))
  

